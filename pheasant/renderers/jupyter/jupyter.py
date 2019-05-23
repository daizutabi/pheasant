import os
import re
from dataclasses import dataclass, field
from itertools import takewhile
from typing import Dict, Iterator, List, Tuple

from pheasant.core.decorator import commentable, surround
from pheasant.core.renderer import Renderer
from pheasant.renderers.jupyter.filters import get_metadata
from pheasant.renderers.jupyter.ipython import (extra_html, get_extra_module,
                                                latex_display_format,
                                                select_display_data,
                                                select_last_display_data,
                                                select_outputs)
from pheasant.renderers.jupyter.kernel import (format_report, kernels,
                                               output_hook)
from pheasant.utils.progress import ProgressBar, progress_bar_factory


@dataclass
class Cell:
    code: str
    context: Dict[str, str]
    template: str
    valid: bool = field(default=True, init=False)
    cached: bool = field(default=False, compare=False)
    output: str = field(default="", compare=False)
    extra_module: str = field(default="", compare=False)


class CacheMismatchError(BaseException):
    """Raised if the cache doesn't match input code in safe mode."""


class Jupyter(Renderer):
    language: str = "python"
    count: int = field(default=0, init=False)
    cache: List[Cell] = field(default_factory=list, init=False)
    extra_html: str = field(default="", init=False)
    progress_bar: ProgressBar = field(default_factory=progress_bar_factory, init=False)

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>`{3,})(?P<language>\w*) ?(?P<option>.*?)\n"
        r"(?P<code>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"\{\{(?P<code>.+?)\}\}"
    RE_INLINE_CODE_PATTERN = re.compile(INLINE_CODE_PATTERN)

    def init(self):
        self.register(Jupyter.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Jupyter.INLINE_CODE_PATTERN, self.render_inline_code)
        templates = self.set_template(["fenced_code", "inline_code"])
        templates[0].environment.filters["get_metadata"] = get_metadata
        # safe: If True, code must match cache.
        # verbose: 0: no info, 1: output, 2: code and output
        self.set_config(enabled=True, safe=False, verbose=0)

    def enter(self):
        self.count = 0
        self.progress_bar.total = len(self.findall())
        self.cache, self.extra_html = self.page.cache.load() or ([], "")

    def exit(self):
        self.progress_bar.finish(count=self.count)
        extra_modules = set(self.get_extra_modules())
        if extra_modules:
            self.extra_html = extra_html(extra_modules)
        self.page.meta["extra_html"] = self.extra_html

        if self.config["enabled"] and self.page.path and self.cache:
            for cell in self.cache:
                cell.cached = True
            self.page.cache.save((self.cache, self.extra_html))

    def get_extra_modules(self) -> Iterator[str]:
        for cell in self.cache:
            if cell.extra_module and not cell.cached:  # New extra module only.
                for cell in self.cache:
                    if cell.extra_module:
                        yield cell.extra_module
                break

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        context["code"] = context["code"].replace("  # isort:skip", "")
        code = context["code"]
        if code.startswith("# option:"):
            index = code.index("\n")
            option, code = code[9:index], code[index + 1 :]
            context["option"] = " ".join([option, context["option"]]).strip()
            context["code"] = code
        if "inline" in context["option"]:
            option = context["option"] + " fenced-code"
            splitter.send("{{" + code + "#" + option + "}}")
            return
        yield "\n" + self.execute_and_render(code, context, "fenced_code") + "\n\n"

    @commentable("code")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        code, context["option"] = split_option(context["code"])
        if "inspect" in context["option"]:
            source = f"\n```python inspect hide-input\n{code}\n```\n"
            splitter.send(source)
            return
        elif "fenced-code" not in context["option"]:
            code = code.replace(";", "\n")
        yield self.execute_and_render(code, context, "inline_code")

    def execute_and_render(self, code, context, template) -> str:
        self.count += 1

        cell = Cell(code, context, template)
        if len(self.cache) >= self.count:
            cached = self.cache[self.count - 1]
            if "freeze" in context["option"] or cell == cached:
                if self.page.path and (self.count - 1) % 5 == 0:
                    relpath = os.path.relpath(self.page.path)
                    self.progress_bar.progress(relpath, count=self.count)
                return surround(cached.output, "cached")
            elif self.page.path and self.config["safe"]:
                self.page.cache.delete()
                self.progress_bar.finish(done=False)
                raise CacheMismatchError

        if not self.config["enabled"]:
            report = {"count": self.count}
            return self.render(template, context, outputs=[], report=report)

        self.language = context.get("language", self.language)
        kernel_name = kernels.get_kernel_name(self.language)

        if not kernel_name:
            report = {"count": self.count}
            cell.output = self.render(template, context, outputs=[], report=report)
            self.update_cache(cell)
            return cell.output

        kernel = kernels.get_kernel(kernel_name)
        kernel.start(silent=self.page.path == "")

        if self.count == 1:
            self.progress_bar.progress("Start", count=self.count)

        kwargs = ""
        if self.language == "python":
            _, kwargs = split_kwargs_from_option(context["option"])
            if kwargs:
                kernel.execute(
                    "from pheasant.renderers.jupyter.ipython import formatter_kwargs\n"
                    f"formatter_kwargs.update(dict({kwargs}))"
                )

        verbose = self.config["verbose"]

        def execute():
            if verbose >= 2:
                codes = [self.language + "> " + line for line in code.split("\n")]
                print("\n".join(codes))
            func = kernel.inspect if "inspect" in context["option"] else kernel.execute
            try:
                outputs = func(code, output_hook=output_hook if verbose else None)
            except NameError:
                if self.page.path:
                    self.page.cache.delete()
                    self.progress_bar.finish(done=False)
                raise NameError(f"Cell number: {self.count}\n{context['code']}")
            report = format_report(kernel.report)
            report["count"] = self.count
            return outputs, report

        def format(result):
            relpath = os.path.relpath(self.page.path)
            return f"{relpath}({result[1]['total']})"

        outputs, report = self.progress_bar.progress(execute, format, self.count)

        if kwargs:
            kernel.execute(
                "from pheasant.renderers.jupyter.ipython import formatter_kwargs\n"
                "formatter_kwargs.clear()"
            )

        cell.extra_module = get_extra_module(outputs)
        select_display_data(outputs)

        if "debug" in context["option"]:
            outputs = [{"type": "execute_result", "data": {"text/plain": outputs}}]
        elif "display-last" in context["option"]:
            select_last_display_data(outputs)
        elif template == "inline_code":
            select_outputs(outputs)
        else:
            latex_display_format(outputs)

        def not_system_exit(output):
            return output["type"] != "error" or output["ename"] != "SystemExit"

        outputs = list(takewhile(not_system_exit, outputs))
        option = context["option"].split()
        code = context["code"].replace("\n\n", "\n")
        cell.output = self.render(
            template,
            context,
            code=code,
            option=option,
            kernel_name=kernel_name,
            outputs=outputs,
            report=report,
        )
        self.update_cache(cell)
        return cell.output

    def update_cache(self, cell: Cell) -> None:
        if len(self.cache) == self.count - 1:
            self.cache.append(cell)
            return

        self.cache[self.count - 1] = cell
        if len(self.cache) > self.count:
            if "freeze" not in cell.context["option"]:
                self.cache[self.count].valid = False


def split_option(code: str) -> Tuple[str, str]:
    if "#" not in code:
        return code, ""
    code, option = code.split("#")
    return code.strip(), option.strip()


# TODO: kwargs which contains space.
def split_kwargs_from_option(option: str) -> Tuple[str, str]:
    if "=" not in option:
        return option, ""
    options = option.split(" ")
    option_list = []
    kwargs_list = []
    for x in options:
        if "=" in x:
            kwargs_list.append(x)
        elif x:
            option_list.append(x)

    return " ".join(option_list), ",".join(kwargs_list)

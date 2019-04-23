import os
import re
from dataclasses import dataclass, field
from itertools import takewhile
from typing import Dict, Iterator, List

from pheasant.core.decorator import commentable, surround
from pheasant.core.renderer import Renderer
from pheasant.renderers.jupyter.ipython import (extra_html, get_extra_module,
                                                latex_display_format,
                                                select_display_data,
                                                select_outputs)
from pheasant.renderers.jupyter.kernel import format_report, kernels
from pheasant.utils.cache import delete_cache, load_cache, save_cache
from pheasant.utils.progress import ProgressBar


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
    option: str = field(default="", init=False)
    count: int = field(default=0, init=False)
    cache: List[Cell] = field(default_factory=list, init=False)
    extra_html: str = field(default="", init=False)
    progress_bar: ProgressBar = field(default_factory=ProgressBar, init=False)
    enabled: bool = field(default=True, init=False)
    safe: bool = field(default=False, init=False)  # If True, code must match cache.

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>`{3,})(?P<language>\w*) ?(?P<option>.*?)\n"
        r"(?P<code>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"\{\{(?P<code>.+?)\}\}"
    RE_INLINE_CODE_PATTERN = re.compile(INLINE_CODE_PATTERN)

    def init(self):
        self.register(Jupyter.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Jupyter.INLINE_CODE_PATTERN, self.render_inline_code)
        self.set_template(["fenced_code", "inline_code"])

    def enter(self):
        self.count = 0
        self.progress_bar.total = len(self.findall())
        self.cache, self.extra_html = load_cache(self.page.path) or ([], "")

    def exit(self):
        self.progress_bar.finish(self.count)
        extra_modules = set(self.get_extra_modules())
        if extra_modules:
            self.extra_html = extra_html(extra_modules)
        self.page.meta["extra_html"] = self.extra_html

        if self.enabled and self.page.path and self.cache:
            for cell in self.cache:
                cell.cached = True
            save_cache(self.page.path, (self.cache, self.extra_html))

    def get_extra_modules(self) -> Iterator[str]:
        for cell in self.cache:
            if cell.extra_module and not cell.cached:  # New extra module only.
                for cell in self.cache:
                    if cell.extra_module:
                        yield cell.extra_module
                break

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        code = context["code"]
        if code.startswith("# option:"):
            index = code.index("\n")
            option = code[9:index].strip()
            if context["option"]:
                context["option"] = " ".join([context["option"], option])
            else:
                context["option"] = option
            code = code[index + 1 :]
            context["code"] = code
        if "inline" in context["option"]:
            self.option = context["option"] + " fenced-code"
            splitter.send("{{" + code + "}}")
            self.option = ""
            return
        if "debug" in context["option"]:
            context["code"] = code
        yield "\n" + self.execute_and_render(code, context, "fenced_code") + "\n\n"

    @commentable("code")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        context["option"] = self.option
        code = context["code"]
        if "fenced-code" not in self.option:
            code = code.replace(";", "\n")
        yield self.execute_and_render(code, context, "inline_code")

    def execute_and_render(self, code, context, template) -> str:
        self.count += 1

        cell = Cell(code, context, template)
        if len(self.cache) >= self.count and "run" not in context["option"]:
            cached = self.cache[self.count - 1]
            if cell == cached:
                if (self.count - 1) % 5 == 0 and self.page.path:
                    relpath = os.path.relpath(self.page.path)
                    self.progress_bar.progress(relpath, count=self.count)
                return surround(cached.output, "cached")
            elif self.safe and self.page.path:
                delete_cache(self.page.path)
                self.progress_bar.finish(finish=False)
                raise CacheMismatchError

        if not self.enabled:
            return self.render(
                template, context, outputs=[], report={"count": self.count}
            )

        language = context.get("language", kernels.language)
        kernel_name = kernels.get_kernel_name(language)

        if not kernel_name:
            return self.render(
                template, context, outputs=[], report={"count": self.count}
            )

        kernel = kernels.get_kernel(kernel_name)
        kernel.start(silent=self.page.path == "")

        if self.count == 1:
            self.progress_bar.progress("Start", count=self.count)

        def execute():
            outputs = kernel.execute(code)
            report = format_report(kernel.report)
            report["count"] = self.count
            return outputs, report

        def format(result):
            relpath = os.path.relpath(self.page.path)
            return f"{relpath} ({result[1]['total']})"

        outputs, report = self.progress_bar.progress(execute, format, self.count)

        cell.extra_module = get_extra_module(outputs)
        select_display_data(outputs)

        if "debug" in context["option"]:
            outputs = [{"type": "execute_result", "data": {"text/plain": outputs}}]
        elif template == "inline_code":
            select_outputs(outputs)
        else:
            latex_display_format(outputs)

        def not_system_exit(output):
            return output["type"] != "error" or output["ename"] != "SystemExit"

        outputs = list(takewhile(not_system_exit, outputs))
        cell.output = self.render(
            template, context, kernel_name=kernel_name, outputs=outputs, report=report
        )

        if len(self.cache) == self.count - 1:
            self.cache.append(cell)
        else:
            self.cache[self.count - 1] = cell
            if len(self.cache) > self.count:
                self.cache[self.count].valid = False
        return cell.output

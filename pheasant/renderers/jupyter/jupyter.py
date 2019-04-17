import ast
import os
import pickle
import re
from dataclasses import dataclass, field
from itertools import takewhile
from typing import Dict, Iterator, List, Optional

from pheasant.core.decorator import comment, surround
from pheasant.core.renderer import Renderer
from pheasant.renderers.jupyter.client import (execute, find_kernel_names,
                                               format_execution_report,
                                               reset_execution_time,
                                               start_kernel)
from pheasant.renderers.jupyter.display import (extra_html, get_extra_module,
                                                latex_display_format,
                                                select_display_data,
                                                select_outputs)
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


class Jupyter(Renderer):
    language: str = "python"
    option: str = field(default="", init=False)
    count: int = field(default=0, init=False)
    cache: List[Cell] = field(default_factory=list, init=False)
    extra_html: str = field(default="", init=False)
    progress_bar: ProgressBar = field(default_factory=ProgressBar, init=False)

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
        self.config["kernel_name"] = {
            key: values[0] for key, values in find_kernel_names().items()
        }

    def enter(self):
        self.count = 0
        self.cache = []
        self.extra_html = ""
        self.progress_bar.total = len(self.findall())

        reset_execution_time()
        path = cache_path(self.page.path)
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.cache, self.extra_html = pickle.load(f)

    def exit(self):
        self.progress_bar.finish(self.count)
        extra_modules = set(self.get_extra_modules())
        if extra_modules:
            self.extra_html = extra_html(extra_modules)
        self.page.meta["extra_html"] = self.extra_html

        if self.page.path and self.cache:
            for cell in self.cache:
                cell.cached = True
            path = cache_path(self.page.path)
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.mkdir(directory)
            with open(path, "wb") as f:
                pickle.dump((self.cache, self.extra_html), f)

    def get_extra_modules(self) -> Iterator[str]:
        for cell in self.cache:
            if cell.extra_module and not cell.cached:  # New extra module.
                for cell in self.cache:
                    if cell.extra_module:
                        yield cell.extra_module
                break

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        if not context["language"]:
            context["language"] = self.language
        else:
            self.language = context["language"]
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
        if self.language == "python" and "text" not in context["option"]:
            code = replace_for_display(code)
        if "debug" in context["option"]:
            context["code"] = code
        yield "\n" + self.execute_and_render(code, context, "fenced_code") + "\n\n"

    @comment("code")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        context["option"] = self.option
        context["language"] = self.language
        code = context["code"]
        if "fenced-code" not in self.option:
            code = code.replace(";", "\n")
        if self.language == "python":
            code = replace_for_display(code)
        yield self.execute_and_render(code, context, "inline_code")

    def progress_format(self, result):
        report = result[1]
        relpath = os.path.relpath(self.page.path)
        return f"{relpath} ({report['page']})"
        # return f"{self.relpath}: Page {report['page']} Total {report['total']}"

    def execute_and_render(self, code, context, template) -> str:
        self.count += 1

        cell = Cell(code, context, template)
        if len(self.cache) >= self.count and "run" not in context["option"]:
            cached = self.cache[self.count - 1]
            if cell == cached:
                if self.progress_bar.total and (self.count - 1) % 5 == 0:
                    relpath = os.path.relpath(self.page.path)
                    self.progress_bar.progress(relpath, count=self.count)
                return surround(cached.output, "cached")

        language = context["language"]
        kernel_name = self.config["kernel_name"].get(language)
        if kernel_name:
            if language == "python":
                init_code = "import pheasant.renderers.jupyter.display"
            else:
                init_code = ""
            start_kernel(kernel_name, init_code)

        if self.progress_bar.total and self.count == 1:
            self.progress_bar.progress("Start", count=self.count)

        def execute():
            outputs = self.execute(code, kernel_name)
            report = format_execution_report()
            report["count"] = self.count
            return outputs, report

        if self.progress_bar.total:
            outputs, report = self.progress_bar.progress(
                execute, self.progress_format, count=self.count
            )
        else:
            outputs, report = execute()

        cell.extra_module = get_extra_module(outputs)
        select_display_data(outputs)

        if "debug" in context["option"]:
            outputs = [{"type": "execute_result", "data": {"text/plain": outputs}}]
        elif template == "inline_code":
            outputs = select_outputs(outputs)
        else:
            latex_display_format(outputs)

        def not_system_exit(output):
            return output["type"] != "error" or output["ename"] != "SystemExit"

        outputs = list(takewhile(not_system_exit, outputs))
        cell.output = self.render(template, context, outputs=outputs, report=report)

        if len(self.cache) == self.count - 1:
            self.cache.append(cell)
        else:
            self.cache[self.count - 1] = cell
            if len(self.cache) > self.count:
                self.cache[self.count].valid = False
        return cell.output

    def execute(
        self, code: str, kernel_name: Optional[str] = None, language: str = "python"
    ) -> List:
        try:
            outputs = execute(code, kernel_name, language)
        except ValueError:
            return []
        return outputs


def replace_for_display(code: str) -> str:
    """Replace a match object with `display` function.

    Parameters
    ----------
    code
        The code to be executed in the inline mode.

    Returns
    -------
    codes, replaced
        Replaced python code list.
    """
    if code.startswith("^"):
        code = code[1:]
        output = "html"
    else:
        output = "markdown"

    try:
        node = ast.parse(code).body[-1]  # type: ignore
    except SyntaxError:
        return code

    if not isinstance(node, ast.Expr):
        return code

    lines = code.split("\n")
    precode = "\n".join(lines[: node.lineno - 1])
    if precode:
        precode += "\n"
    code_gen = (line for line in lines[node.lineno - 1 :] if not line.startswith("#"))
    code = "\n".join(code_gen)
    code = f"__pheasant_dummy__ = {code}\n"

    display = "pheasant.renderers.jupyter.display.display"
    return f'{precode}{code}{display}(__pheasant_dummy__, output="{output}")'


def cache_path(path):
    directory, path = os.path.split(path)
    return os.path.join(directory, ".pheasant_cache", path + ".cache")

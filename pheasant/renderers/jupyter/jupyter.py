import ast
import datetime
import os
import pickle
import re
from dataclasses import dataclass, field
from itertools import takewhile
from typing import Dict, Iterator, List, Optional

from pheasant.core.base import format_timedelta
from pheasant.core.decorator import comment, surround
from pheasant.core.renderer import Renderer
from pheasant.renderers.jupyter.client import (execute, execution_report,
                                               find_kernel_names,
                                               restart_kernel, start_kernel)
from pheasant.renderers.jupyter.display import (EXTRA_MODULES, extra_html,
                                                extra_resources,
                                                select_display_data)
from pheasant.renderers.jupyter.progress import ProgressBar


@dataclass
class Cell:
    code: str
    context: Dict[str, str]
    template: str
    valid: bool = field(default=True, init=False)
    output: str = field(default="", compare=False)


class Jupyter(Renderer):
    language: str = "python"
    option: str = field(default="", init=False)
    cursor: int = field(default=0, init=False)
    cache: Dict[str, List[Cell]] = field(default_factory=dict, init=False)
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

    def reset(self):
        self.cursor = 0
        self.progress_bar.count = 0
        self.progress_bar.total = 0
        execution_report["page"] = datetime.timedelta(0)

    def reset_source(self, source):
        self.reset()
        self.progress_bar.total = self.bare_execute_count(source)

    @property
    def src_path(self) -> str:
        return self._src_path

    @src_path.setter
    def src_path(self, src_path: str) -> None:
        self._src_path = src_path
        if not src_path:
            return
        path = cache_path(src_path)
        if os.path.exists(path):
            with open(path, "rb") as f:
                cache, meta = pickle.load(f)

            self.cache[src_path] = cache
            if meta:
                self.meta[src_path] = meta

    def dump(self):
        for src_path, cache in self.cache.items():
            if not src_path or not cache:
                continue
            meta = self.meta.get(src_path)
            path = cache_path(src_path)
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.mkdir(directory)
            with open(path, "wb") as f:
                pickle.dump((cache, meta), f)

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
        if context["code"].strip() == "!restart":
            kernel_name = self.config["kernel_name"][self.language]
            restart_kernel(kernel_name)
            self.src_path = ""
            self.reset()
            return

        context["option"] = self.option
        context["language"] = self.language
        code = context["code"]
        if "fenced-code" not in self.option:
            code = code.replace(";", "\n")
        if self.language == "python":
            code = replace_for_display(code)
        yield self.execute_and_render(code, context, "inline_code")

    def execute_and_render(self, code, context, template) -> str:
        self.cursor += 1
        cell = Cell(code, context, template)
        cache = self.cache.setdefault(self.src_path, [])
        if len(cache) >= self.cursor and "run" not in context["option"]:
            cached = cache[self.cursor - 1]
            if cell == cached:
                if self.progress_bar.total:
                    self.progress_bar.count += 1
                return surround(cached.output, "cached")

        language = context["language"]
        kernel_name = self.config["kernel_name"].get(language)
        if kernel_name:
            if language == "python":
                init_code = "import pheasant.renderers.jupyter.display"
            else:
                init_code = ""
            start_kernel(kernel_name, init_code)

        def execute():
            outputs = self.execute(code, kernel_name)
            report = format_report()
            report["cursor"] = self.cursor
            return outputs, report

        def format(result):
            report = result[1]
            return f"page: {report['page']:>8}, total: {report['total']:>8}"

        if self.progress_bar.total:
            outputs, report = self.progress_bar.progress(execute, format)
        else:
            outputs, report = execute()

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
        if len(cache) == self.cursor - 1:
            cache.append(cell)
        else:
            cache[self.cursor - 1] = cell
            if len(cache) > self.cursor:
                cache[self.cursor].valid = False
        return cell.output

    def execute(
        self, code: str, kernel_name: Optional[str] = None, language: str = "python"
    ) -> List:
        try:
            outputs = execute(code, kernel_name, language)
        except ValueError:
            return []
        self.update_extra_module(outputs)
        select_display_data(outputs)
        return outputs

    def update_extra_module(self, outputs: List[dict]) -> None:
        extra = self.meta.setdefault(self.src_path, {"extra_module": set()})

        if len(extra["extra_module"]) == len(EXTRA_MODULES):
            return

        for output in outputs:
            if (
                "data" in output
                and ("text/html" in output["data"] or "text/latex" in output["data"])
                and "text/plain" in output["data"]
            ):
                module = output["data"]["text/plain"]
                if module in EXTRA_MODULES:
                    extra["extra_module"].add(module)

    @property
    def extra_html(self) -> str:
        extra = self.meta.get(self.src_path, None)
        if extra is None:
            return ""

        extra = extra_resources(extra["extra_module"])
        return extra_html(extra)

    @classmethod
    def bare_execute_count(cls, source):
        fenced = re.findall(cls.FENCED_CODE_PATTERN, source, re.MULTILINE | re.DOTALL)
        inline = re.findall(cls.INLINE_CODE_PATTERN, source)
        return len(fenced) + len(inline)


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


def select_outputs(outputs: List):
    for output in outputs:
        if "data" in output and "text/plain" in output["data"]:
            text = output["data"]["text/plain"]
            if (text.startswith('"') and text.endswith('"')) or (
                text.startswith("'") and text.endswith("'")
            ):
                output["data"]["text/plain"] = ast.literal_eval(text)
    for output in outputs:
        if output["type"] == "display_data":
            outputs = [output for output in outputs if output["type"] == "display_data"]
            break
    return outputs


def latex_display_format(outputs: List) -> None:
    for output in outputs:
        if "data" in output and "text/latex" in output["data"]:
            text = output["data"]["text/latex"]
            output["data"]["text/latex"] = f"$${text}$$"


def format_report():
    report = dict(execution_report)
    if "start" not in report:
        return {}

    datetime_format = r"%Y-%m-%d %H:%M:%S"
    report["start"] = report["start"].strftime(datetime_format)
    report["end"] = report["end"].strftime(datetime_format)
    report["cell"] = format_timedelta(report["cell"])
    report["page"] = format_timedelta(report["page"])
    report["total"] = format_timedelta(report["total"])
    report["count"] = report["execution_count"]
    return report


def cache_path(src_path):
    directory, path = os.path.split(src_path)
    directory = os.path.join(directory, ".pheasant_cache")
    return os.path.join(directory, path + ".cache")

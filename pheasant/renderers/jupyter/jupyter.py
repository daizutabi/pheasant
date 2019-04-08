import ast
import datetime
import re
from dataclasses import dataclass, field
from itertools import takewhile
from typing import Dict, Iterator, List

from pheasant.core.base import format_timedelta
from pheasant.core.decorator import comment, surround
from pheasant.core.renderer import Renderer
from pheasant.renderers.jupyter.client import (execute, execution_report,
                                               find_kernel_names,
                                               restart_kernel)
from pheasant.renderers.jupyter.display import (EXTRA_MODULES, extra_html,
                                                extra_resources,
                                                select_display_data)


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
    active: bool = field(default=True, init=False)
    cursor: int = field(default=0, init=False)
    total: int = field(default=0, init=False)
    cache: Dict[str, List[Cell]] = field(default_factory=dict, init=False)

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
        execution_report["page"] = datetime.timedelta(0)

    def activate(self):
        self.active = True
        self.total = self.cursor
        self.reset()

    def deactivate(self):
        self.active = False
        self.total = 0
        self.reset()

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
            self.cache = {}
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
        if not self.active:
            return "XXX"
        cell = Cell(code, context, template)
        cache = self.cache.setdefault(self.abs_src_path, [])
        if len(cache) >= self.cursor and "run" not in context["option"]:
            cached = cache[self.cursor - 1]
            if cell == cached:
                return surround(cached.output, "cached")

        outputs = self.execute(code, context["language"])
        report = format_report()
        report["cursor"] = self.cursor
        if self.total:
            progress_bar(self, report)

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

    def execute(self, code: str, language: str = "python") -> List:
        if language not in self.config["kernel_name"]:
            return []
        kernel_name = self.config["kernel_name"][language]
        if self.cursor == 1 and language == "python":
            execute("import pheasant.renderers.jupyter.display", kernel_name)
        outputs = execute(code, kernel_name)
        self.update_extra_module(outputs)
        select_display_data(outputs)
        return outputs

    def update_extra_module(self, outputs: List[dict]) -> None:
        extra = self.meta.setdefault(self.abs_src_path, {"extra_module": set()})

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
        extra = self.meta.get(self.abs_src_path, None)
        if extra is None:
            return ""

        extra = extra_resources(extra["extra_module"])
        return extra_html(extra)


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
    datetime_format = r"%Y-%m-%d %H:%M:%S"
    report["start"] = report["start"].strftime(datetime_format)
    report["end"] = report["end"].strftime(datetime_format)
    report["cell"] = format_timedelta(report["cell"])
    report["page"] = format_timedelta(report["page"])
    report["total"] = format_timedelta(report["total"])
    report["count"] = report["execution_count"]
    return report


def progress_bar(jupyter, report):
    if jupyter.cursor > jupyter.total:
        return
    length = 50
    current = int(length * min(jupyter.cursor / jupyter.total, 1))
    count = str(report["count"]).zfill(4)
    if current >= length:
        bar = "[" + "=" * length + "=]"
    else:
        bar = "[" + "=" * current + ">" + "-" * (length - current) + "]"
    cursor = str(jupyter.cursor).zfill(3)
    total = str(jupyter.total).zfill(3)
    count = f"[{count}]"
    progress = f"{cursor}/{total}"
    time = f"{report['cell']:>8} {report['page']:>8} {report['total']:>8}"

    line = " ".join([count, bar, progress, time])
    print("\r" + line, end="")
    if jupyter.cursor == jupyter.total:
        print()

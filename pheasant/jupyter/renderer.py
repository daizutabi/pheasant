import re
from ast import literal_eval
from typing import Iterator, List, Match

from pheasant.core.decorator import comment
from pheasant.core.renderer import Renderer
from pheasant.jupyter.client import (execute, execution_report,
                                     find_kernel_names)
from pheasant.jupyter.display import (bokeh_extra_resources,
                                      holoviews_extra_resources,
                                      select_display_data)


class Jupyter(Renderer):

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>`{3,})(?P<language>\w+) ?(?P<option>.*?)\n"
        r"(?P<code>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"\{\{(?P<code>.+?)\}\}"
    RE_INLINE_CODE_PATTERN = re.compile(INLINE_CODE_PATTERN)

    def __post_init__(self):
        super().__post_init__()
        self.register(Jupyter.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Jupyter.INLINE_CODE_PATTERN, self.render_inline_code)
        self.set_template(["fenced_code", "inline_code"])
        self.config["kernel_name"] = {
            key: values[0] for key, values in find_kernel_names().items()
        }
        self.reset()

    def setup(self):
        codes = [
            "import pheasant.jupyter.display",
            "import pandas",
            "pandas.options.display.max_colwidth = 0",
        ]
        code = "\n".join(codes)
        self.execute(code, "python")

    def reset(self):
        for key in ["css", "javascript", "raw_css", "raw_javascript"]:
            self.meta[f"extra_{key}"] = []
        self.meta["extra_module"] = []

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        code = context["code"]
        if "display" in context["option"]:
            code = replace_for_display(code, skip_equal=False)
        if "inline" in context["option"]:
            code = replace_fenced_code_for_display(code)
            code = replace_for_display(code, skip_equal=False)
        # context["code"] = code  # Uncomment for debug
        outputs = self.execute(code, context["language"])
        report = format_report()
        yield self.render("fenced_code", context, outputs=outputs, report=report) + "\n"

    @comment("code")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        code = replace_for_display(context["code"])
        if "language" not in context:
            context["language"] = "python"

        outputs = self.execute(code, context["language"])
        outputs = select_outputs(outputs)
        yield self.render("inline_code", context, outputs=outputs)

    def execute(self, code: str, language: str = "python") -> List:
        if language not in self.config["kernel_name"]:
            return []
        outputs = execute(code, self.config["kernel_name"][language])
        self.update_extra_resourse(outputs)
        select_display_data(outputs)
        return outputs

    def update_extra_resourse(self, outputs: List[dict]) -> None:
        module_dict = {
            "bokeh": bokeh_extra_resources,
            "holoviews": holoviews_extra_resources,
        }
        if len(self.meta["extra_module"]) == len(module_dict):
            return

        new_modules = []
        for output in outputs:
            if (
                "data" in output
                and "text/html" in output["data"]
                and "text/plain" in output["data"]
            ):
                module = output["data"]["text/plain"]
                if (
                    module in module_dict.keys()
                    and module not in self.meta["extra_module"]
                ):
                    new_modules.append(module)

        for module in new_modules:
            self.meta["extra_module"].append(module)
            resources = module_dict[module]()
            for key, values in resources.items():
                self.meta[key].extend(
                    value for value in values if value not in self.meta[key]
                )


def replace_fenced_code_for_display(code: str) -> str:
    def replace(match: Match) -> str:
        return replace_for_display(match.group(1), skip_equal=False)

    return Jupyter.RE_INLINE_CODE_PATTERN.sub(replace, code)


def replace_for_display(code: str, skip_equal: bool = True) -> str:
    """Replace a match object with `display` function.

    Parameters
    ----------
    code
        The code to be executed in the inline mode.
    skip_equal
        If True, skip the statement which contains equal character.

    Returns
    -------
    codes
        Replaced python code list.
    """
    if "=" in code and skip_equal:
        return code

    if code.startswith("^"):
        code = code[1:]
        output = "html"
    else:
        output = "markdown"

    code = code.replace(";", "\n")
    if "\n" not in code:
        precode = ""
    else:
        codes = code.split("\n")
        if codes[-1].startswith(" "):
            return code
        match = re.match(r"(\w+) *?=", codes[-1])
        if match:
            code = match.group(1)
        else:
            code = "_pheasant_dummy"
            codes[-1] = f"{code} = {codes[-1]}"
        precode = "\n".join(codes) + "\n"

    return f'{precode}pheasant.jupyter.display.display({code}, output="{output}")'


def select_outputs(outputs):
    for output in outputs:
        if "data" in output and "text/plain" in output["data"]:
            text = output["data"]["text/plain"]
            if (text.startswith('"') and text.endswith('"')) or (
                text.startswith("'") and text.endswith("'")
            ):
                output["data"]["text/plain"] = literal_eval(text)
    for output in outputs:
        if output["type"] == "display_data":
            outputs = [output for output in outputs if output["type"] == "display_data"]
            break
    return outputs


def format_report():
    report = dict(execution_report)
    datetime_format = r"%Y-%m-%d %H:%M:%S"
    report["start"] = report["start"].strftime(datetime_format)
    report["end"] = report["end"].strftime(datetime_format)
    report["elasped"] = timedelta_format(report["elasped"])
    report["total"] = timedelta_format(report["total"])
    report["count"] = report["execution_count"]
    return report


def timedelta_format(dt) -> str:
    sec = dt.total_seconds()
    if sec >= 3600:
        return f"{sec//3600}h{sec//60%60}min{sec%3600%60}s"
    elif sec >= 60:
        return f"{sec//60}min{sec%60}s"
    elif sec >= 10:
        return f"{sec:0.1f}s"
    elif sec >= 1:
        return f"{sec:0.2f}s"
    elif sec >= 1e-1:
        return f"{sec*1e3:.00f}ms"
    elif sec >= 1e-2:
        return f"{sec*1e3:.01f}ms"
    elif sec >= 1e-3:
        return f"{sec*1e3:.02f}ms"
    elif sec >= 1e-4:
        return f"{sec*1e6:.00f}us"
    elif sec >= 1e-5:
        return f"{sec*1e6:.01f}us"
    elif sec >= 1e-6:
        return f"{sec*1e6:.02f}us"
    else:
        return f"{sec*1e9:.00f}ns"

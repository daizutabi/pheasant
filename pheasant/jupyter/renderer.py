import re
from ast import literal_eval
from typing import Any, Dict, Iterable, List, Match, Optional

from pheasant.core import markdown
from pheasant.core.parser import Parser
from pheasant.core.renderer import Config, Context, Renderer
from pheasant.jupyter.client import execute, find_kernel_names


class Jupyter(Renderer):

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>`{3,}|~{3,})(?P<language>\w+) ?(?P<option>.*?)\n"
        r"(?P<code>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"\{\{(?P<code>.+?)\}\}"
    RE_INLINE_CODE_PATTERN = re.compile(INLINE_CODE_PATTERN)

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        self.register(Jupyter.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Jupyter.INLINE_CODE_PATTERN, self.render_inline_code)
        self.set_template(["fenced_code", "inline_code"])
        if "kernel_name" not in self.config:
            self.config["kernel_name"] = {
                key: values[0] for key, values in find_kernel_names().items()
            }

    def init(self) -> None:
        code = "\n".join(
            [
                "import importlib",
                "import inspect",
                "import pheasant.jupyter.display",
                "import pandas",
                "pandas.options.display.max_colwidth = 0",
            ]
        )
        self.execute(code, "python")

    def render_fenced_code(self, context: Context, parser: Parser) -> Iterable[str]:
        if "inline" in context["option"]:
            context["code"] = preprocess_fenced_code(context["code"])
        yield self.render(context, self.config["fenced_code_template"])

    def render_inline_code(self, context: Context, parser: Parser) -> Iterable[str]:
        context["code"] = preprocess_inline_code(context["code"])
        yield self.render(context, self.config["inline_code_template"])

    def render(self, context: Dict[str, Any], template) -> str:
        outputs = self.execute(code=context["code"], language=context["language"])
        context.update(outputs=outputs, config=self.config)
        return template.render(**context)

    def execute(self, code: str, language: str = "python") -> List:
        if language not in self.config["kernel_name"]:
            return []
        outputs = execute(code, self.config["kernel_name"][language])
        select_display_data(outputs)
        return outputs

        # 3type: stream, name: stdout, text: output
        # 3type: error, ename, evalue
        # 3type: execute_result, data:
        # 3type: display_data, data


def preprocess_fenced_code(code: str) -> str:
    def replace(match: Match) -> str:
        return replace_for_display(match.group(1), ignore_equal=True)

    return Jupyter.RE_INLINE_CODE_PATTERN.sub(replace, code)


def preprocess_inline_code(code: str) -> str:
    return replace_for_display(code)


def replace_for_display(code: str, ignore_equal: bool = False) -> str:
    """Replace a match object with `display` function.

    Parameters
    ----------
    code
        The code to be executed in the inline mode.
    ignore_equal
        If True, do not replace the code which contains `=`.

    Returns
    -------
    codes
        Replaced python code list.
    """
    if "=" in code and not ignore_equal:
        return code

    precode = None

    if code.startswith("^"):
        code = code[1:]
        output = "html"
    else:
        output = "markdown"

    if ";" in code:
        codes = code.split(";")
        code = "_pheasant_dummy"
        codes[-1] = f"{code} = {codes[-1]}"
        precode = "\n".join(codes) + "\n"
    else:
        precode = ""

    return f'{precode}pheasant.jupyter.display.display({code}, output="{output}")'


DISPLAY_DATA_PRIORITY = [
    # "application/vnd.jupyter.widget-state+json",
    # "application/vnd.jupyter.widget-view+json",
    "application/javascript",
    "text/html",
    "text/markdown",
    "image/svg+xml",
    "text/latex",
    "image/png",
    "image/jpeg",
    "text/plain",
]


def select_display_data(outputs: List[Dict]) -> None:
    """Select display data with the highest priority."""
    for output in outputs:
        for data_type in DISPLAY_DATA_PRIORITY:
            if "data" in output and data_type in output["data"]:
                text = output["data"][data_type]
                if data_type == "text/html" and '"dataframe"' in text:
                    text = delete_style(text)
                output["data"] = {data_type: text}
                break


PANDAS_PATTERN = re.compile(
    r'(<style scoped>.*?</style>)|( border="1")|( style="text-align: right;")',
    flags=re.DOTALL,
)


def delete_style(html: str) -> str:
    """Delete style from Pandas DataFrame html."""
    return PANDAS_PATTERN.sub("", html)


def strip_text(outputs: list) -> None:
    for output in outputs:
        if output["type"] == "execute_result":
            if "text/html" in output["data"]:
                return
            elif "text/plain" in output["data"]:
                text = output["data"]["text/plain"]
                if text.startswith("'"):
                    text = literal_eval(text)
                output["data"] = {"text/plain": text}
                break

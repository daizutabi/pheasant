"""Render a cell using the Jinja2 template engine."""

import re
from typing import Callable, Optional

from pheasant.jupyter.cache import memoize
from pheasant.jupyter.client import execute
from pheasant.jupyter.config import config


def render_fenced_code(context: dict) -> str:
    """Convert a fenced code into markdown or html."""
    return config["fenced_code_template"].render(**context)


def render_inline_code(context: dict) -> str:
    """Convert an inline code into markdown or html."""
    strip_text(context["outputs"])
    return config["inline_code_template"].render(**context)


# `execute_and_render` function is 'memoize'-decorated in order to cache the
# source and outputs to avoid rerunning the same cell unnecessarily.
@memoize
def execute_and_render(
    code: str,
    render: Callable[[dict], str],
    kernel_name: Optional[str] = None,
    language: str = "python",
    callback: Optional[Callable[[list], None]] = None,
    select_display: bool = True,
    **kwargs
) -> str:
    """Run a code and render the code and outputs into markdown.

    Parameters
    ----------
    code
        The code to execute.
    render
        Rendering function for the code and outputs.
    kernel_name
        Name of a Jupyter kernel to execute the code.
    language
        Languate for a Jupyter kernel.
    callback
        Callback function which is called after code execution.
    select_display
        If True, select display data with the highest priority.
    **kwars:
        Additional parameters for the render function.

    Returun
    -------
    str
        rendered string
    """
    outputs = execute(code, kernel_name=kernel_name, language=language)
    if select_display:
        select_display_data(outputs)
    if callback:
        callback(outputs)
    context = dict(code=code, outputs=outputs, language=language, **kwargs)
    return render(context)


display_data_priority = [
    "application/vnd.jupyter.widget-state+json",
    "application/vnd.jupyter.widget-view+json",
    "application/javascript",
    "text/html",
    "text/markdown",
    "image/svg+xml",
    "text/latex",
    "image/png",
    "image/jpeg",
    "text/plain",
]


def select_display_data(outputs: list) -> None:
    """Select display data with the highest priority."""
    for output in outputs:
        for data_type in display_data_priority:
            if "data" in output and data_type in output["data"]:
                text = output["data"][data_type]
                if data_type == "text/html" and '"dataframe"' in text:
                    text = delete_style(text)
                output["data"] = {data_type: text}
                break


def strip_text(outputs: list) -> None:
    for output in outputs:
        if output["type"] == "execute_result":
            if "text/html" in output["data"]:
                return
            elif "text/plain" in output["data"]:
                text = output["data"]["text/plain"]
                if text.startswith("'"):
                    text = eval(text)
                output["data"] = {"text/plain": text}
                break


PANDAS_PATTERN = (
    r'(<style scoped>.*?</style>)|( border="1")|' r'( style="text-align: right;")'
)
pandas_re_compile = re.compile(PANDAS_PATTERN, flags=re.DOTALL)


def delete_style(html: str) -> str:
    """Delete style from Pandas DataFrame html."""
    return re.sub(pandas_re_compile, "", html)

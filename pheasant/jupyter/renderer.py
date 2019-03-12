"""Render a cell using the Jinja2 template engine."""

import re
from ast import literal_eval
from typing import Callable, Dict, Optional

from pheasant.jupyter.kernel import execute

# from pheasant.jupyter.cache import memoize


# `execute_and_render` function is 'memoize'-decorated in order to cache the source and
# outputs to avoid rerunning the same cell unnecessarily.
# @memoize
def execute_and_render(
    render: Callable[..., str],
    code: str = "",
    kernel_name: Optional[str] = None,
    language: str = "python",
    callback: Optional[Callable[[list], None]] = None,
    select_display: bool = True,
    strip: bool = False,
    **kwargs: dict
) -> str:
    """Run a code and render the code and outputs into markdown.

    Parameters
    ----------
    render
        Rendering function for the code and outputs.
    code
        The code to execute.
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
    # print(f"Code: >>{code}<<")
    outputs = execute(code, kernel_name=kernel_name, language=language)
    # print(f"Output: >>{outputs}<<")
    if select_display:
        select_display_data(outputs)
    if callback:
        callback(outputs)
    if strip:
        strip_text(outputs)
    context = dict(code=code, outputs=outputs, language=language, **kwargs)
    return render(**context)


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
                    text = literal_eval(text)
                output["data"] = {"text/plain": text}
                break


PANDAS_PATTERN = re.compile(
    r'(<style scoped>.*?</style>)|( border="1")|( style="text-align: right;")',
    re.DOTALL,
)


def delete_style(html: str) -> str:
    """Delete style from Pandas DataFrame html."""
    return re.sub(PANDAS_PATTERN, "", html)


def replace(
    code: str, ignore_equal: bool = False, inline_html_character: str = "^"
) -> str:
    """Replace a match object with `display` function.

    Parameters
    ----------
    code
        The matched code given by the `re.sub` function for an inline cell.
    ignore_equal
        If True, do not replace the code which contains `=`.

    Returns
    -------
    str
        Replaced python code code but has not been executed yet.
    """
    if "=" in code and not ignore_equal:
        return code

    if code.startswith(inline_html_character):
        code = code[1:]
        output = "html"
    else:
        output = "markdown"

    if ";" in code:
        codes = code.split(";")
        code = "_pheasant_dummy"
        codes[-1] = f"{code} = {codes[-1]}"
        execute("\n".join(codes))

    return f'pheasant.jupyter.display.display({code}, output="{output}")'


def update_extra_resources(outputs: list) -> None:
    """Update extra resources in the pheasant config.

    If the `text/plain` output of the cell is `tuple`,
    the first element is the real output of the cell execution
    and the second element is a dictionary to update the extra
    resources in the pheasant config.

    Parameters
    ----------
    outputs
        Outputs of code execution.
    """

    def replace(data: dict) -> None:
        """Replace tuple output to html and register extra resources."""
        display = literal_eval(data["text/plain"])
        if isinstance(display, tuple):
            html, resources = display
            update(resources)
            data["text/html"] = html
            del data["text/plain"]

    def update(resources: dict) -> None:
        """Update extra resources.

        If `source_file` is not specified, global extra_XXXs are updated,
        Otherwise, config['extre_resources'][<source_file>] updated.
        """

        from pheasant.core.config import config as pheasant_config

        source_file = pheasant_config["source_file"]
        if source_file is None:
            config = pheasant_config
        else:
            extra_resources = pheasant_config["extra_resources"]
            if source_file not in extra_resources:
                extra_resources[source_file] = {}
            config = extra_resources[source_file]

        extra_keys = [
            "extra_css",
            "extra_raw_css",
            "extra_javascript",
            "extra_raw_javascript",
        ]

        for key in extra_keys:
            if key not in config:
                config[key] = []
            if key in resources:
                values = [value for value in resources[key] if value not in config[key]]
                if values:
                    config[key].extend(values)

    for output in outputs:
        if output["type"] == "execute_result" and "text/plain" in output["data"]:
            replace(output["data"])

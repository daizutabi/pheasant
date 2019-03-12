import re
from ast import literal_eval
from typing import Match

from pheasant.jupyter.client import execute
from pheasant.jupyter.config import config

# #from pheasant.jupyter.renderer import execute_and_render
# #from pheasant.number import config as config_number


def preprocess_fenced_code(code: str) -> str:
    def replace_(match: Match) -> str:
        return replace(match.group(1), ignore_equal=True)

    return re.sub(config["INLINE_PATTERN"], replace_, code)


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

        from pheasant.config import config as pheasant_config

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

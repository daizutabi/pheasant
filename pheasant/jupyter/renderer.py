import re
from typing import Iterator, List, Match

from pheasant.core.renderer import Renderer
from pheasant.jupyter.client import execute, find_kernel_names
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

    def init(self) -> None:
        code = "\n".join(
            [
                "import pheasant.jupyter.display",
                "import pandas",
                "pandas.options.display.max_colwidth = 0",
            ]
        )
        self.execute(code, "python")

    def reset(self):
        self.config["extra_resources"] = {}
        for key in [
            "module",
            "extra_css",
            "extra_javascript",
            "extra_raw_css",
            "extra_raw_javascript",
        ]:
            self.config["extra_resources"][key] = []

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        if "inline" in context["option"]:
            context["code"] = preprocess_fenced_code(context["code"])
        yield self.render("fenced_code", context)

    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        context["code"] = preprocess_inline_code(context["code"])
        yield self.render("inline_code", context)

    def render(self, template, context, **kawrgs) -> str:
        if 'language' not in context:
            context["language"] = "python"
        outputs = self.execute(code=context["code"], language=context["language"])
        return super().render(template, context, outputs=outputs) + "\n"

    def execute(self, code: str, language: str = "python") -> List:
        if language not in self.config["kernel_name"]:
            return []
        outputs = execute(code, self.config["kernel_name"][language])
        self.update_extra_resourse(outputs)
        select_display_data(outputs)
        return outputs

    def update_extra_resourse(self, outputs):
        module_dict = {
            "bokeh": bokeh_extra_resources,
            "holoviews": holoviews_extra_resources,
        }
        extra_resources = self.config["extra_resources"]
        if len(extra_resources["module"]) == len(module_dict):
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
                    and module not in extra_resources["module"]
                ):
                    new_modules.append(module)

        for module in new_modules:
            extra_resources["module"].append(module)
            resources = module_dict[module]()
            for key in extra_resources:
                if key in resources:
                    extra_resources[key].extend(
                        [
                            value
                            for value in resources[key]
                            if value not in extra_resources[key]
                        ]
                    )


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

"""A module processes inline code.

IMPORTANT: `display` function is called from jupyter kernel.
"""
import base64
import io
import re
from ast import literal_eval
from typing import Any, Callable, Dict, List

from IPython.display import HTML, Latex


class BokehHTML(HTML):
    def __repr__(self):
        return "bokeh"


class HoloviewsHTML(HTML):
    def __repr__(self):
        return "holoviews"


def matplotlib_to_base64(obj, output: str = "markdown") -> str:
    """Convert a Matplotlib's figure into base64 string."""

    if not hasattr(obj, "savefig"):
        obj = obj.figure  # obj is axes.

    buffer = io.BytesIO()
    obj.savefig(buffer, fmt="png", bbox_inches="tight", transparent=True)
    buffer.seek(0)
    binary = buffer.getvalue()
    buffer.close()

    return base64image(binary, "png", output)


def base64image(binary: bytes, fmt: str, output: str) -> str:
    """Return markdown or HTML image source."""
    data = base64.b64encode(binary).decode("utf8")
    data = f"data:image/{fmt};base64,{data}"

    if output == "markdown":
        return f"![{fmt}]({data})"
    elif output == "html":
        return HTML(f'<img alt="{fmt}" src="{data}"/>')
    else:
        raise ValueError(f"Unknown output: {output}")


def pandas_to_html(dataframe, **kwargs) -> HTML:
    """Convert a pandas.DataFrame into a <table> tag."""
    html = dataframe.to_html(escape=False)
    html = delete_style(html)
    return HTML(html)


def sympy_to_latex(obj, **kwargs) -> Latex:
    """Convert a Sympy's object into latex string."""
    import sympy

    return Latex(sympy.latex(obj))


def bokeh_to_html(obj, **kwargs) -> HTML:
    """Convert a Bokeh's obj into <script> and <div> tags."""
    from bokeh.embed import components

    script, div = components(obj)
    return BokehHTML(script + div)


def bokeh_extra_resources() -> Dict[str, List[str]]:
    from bokeh.resources import CDN

    return {"extra_css": CDN.css_files, "extra_javascript": CDN.js_files}


def holoviews_to_html(obj, **kwargs) -> HTML:
    import holoviews as hv

    renderer = hv.renderer("bokeh")
    html = renderer.html(obj, fmt=None)  # fmt=None is important!
    return HoloviewsHTML(html)


def holoviews_extra_resources() -> Dict[str, List[str]]:
    import holoviews as hv

    renderer = hv.renderer("bokeh")
    js_html, css_html = renderer.html_assets()
    return _split_html_assets(js_html, css_html)


def _split_html_assets(js_html: str, css_html: str) -> Dict[str, List[str]]:
    resources = _split_js_html_assets(js_html)
    resources.update(_split_css_html_assets(css_html))
    return resources


def _split_js_html_assets(js_html: str) -> Dict[str, List[str]]:
    pattern = r'<script src="(.*?)" type="text/javascript"></script>'
    extra_javascript = re.findall(pattern, js_html)

    pattern = r'(<script type="text/javascript">.*?</script>)'
    extra_raw_javascript = re.findall(pattern, js_html, re.DOTALL)

    return {
        "extra_javascript": extra_javascript,
        "extra_raw_javascript": extra_raw_javascript,
    }


def _split_css_html_assets(css_html: str) -> Dict[str, List[str]]:
    pattern = r'<link rel="stylesheet" href="(.*?)">'
    extra_css = re.findall(pattern, css_html)

    pattern = r"(<style>.*?</style>)"
    extra_raw_css = re.findall(pattern, css_html, re.DOTALL)

    return {"extra_css": extra_css, "extra_raw_css": extra_raw_css}


def extra_html(extra: Dict[str, List[str]]) -> str:
    return "\n".join(
        [
            f'<link href="{css}" rel="stylesheet"/>'
            for css in extra["extra_css"]
            if "bokeh-" in css
        ]
        + extra["extra_raw_css"]
        + [f'<script src="{js}"></script>' for js in extra["extra_javascript"]]
        + extra["extra_raw_javascript"]
    )


CONVERTERS: Dict[str, Callable] = {
    "matplotlib": matplotlib_to_base64,
    "pandas": pandas_to_html,
    "sympy": sympy_to_latex,
    "bokeh": bokeh_to_html,
    "holoviews": holoviews_to_html,
}


def display(obj: Any, **kwargs: Any) -> Any:
    if hasattr(obj, "__module__"):
        module = obj.__module__.split(".")[0]
        converter = CONVERTERS.get(module, lambda obj: obj)
        return converter(obj, **kwargs)
    else:
        return obj


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

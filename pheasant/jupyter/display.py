"""A module processes inline code.

IMPORTANT: `display` function is called from jupyter kernel.
"""
import base64
import io
import re
from typing import Any, Callable, Dict, List

from IPython.display import HTML, Latex

from pheasant.jupyter.renderer import delete_style


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
    return HTML(script + div)


def bokeh_extra_resources() -> Dict[str, List[str]]:
    from bokeh.resources import CDN

    return {"extra_css": CDN.css_files, "extra_javascript": CDN.js_files}


def holoviews_to_html(obj, **kwargs) -> HTML:
    import holoviews as hv

    renderer = hv.renderer("bokeh")
    html = renderer.html(obj, fmt=None)  # fmt=None is important!
    return HTML(html)


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

    pattern = r'<script type="text/javascript">(.*?)</script>'
    extra_raw_javascript = re.findall(pattern, js_html, re.DOTALL)

    return {
        "extra_javascript": extra_javascript,
        "extra_raw_javascript": extra_raw_javascript,
    }


def _split_css_html_assets(css_html: str) -> Dict[str, List[str]]:
    pattern = r'<link rel="stylesheet" href="(.*?)">'
    extra_css = re.findall(pattern, css_html)

    pattern = r"<style>(.*?)</style>"
    extra_raw_css = re.findall(pattern, css_html, re.DOTALL)

    return {"extra_css": extra_css, "extra_raw_css": extra_raw_css}


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

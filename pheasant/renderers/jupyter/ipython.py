import ast
import json
import re
from typing import Any, Dict, Iterable, List, Tuple

import jinja2
from IPython import get_ipython

PANDAS_PATTERN = re.compile(
    r'(<style scoped>.*?</style>)|( border="1")|( style="text-align: right;")',
    flags=re.DOTALL,
)

formatter_kwargs: Dict[str, Any] = {}


def pandas_dataframe_to_html(obj) -> str:
    """Convert a pandas.DataFrame into a <table> tag."""
    html = obj.to_html(escape=False)
    return PANDAS_PATTERN.sub("", html)


def pandas_series_to_html(obj) -> str:
    """Convert a pandas.DataFrame into a <table> tag."""
    series = obj.copy()
    if not series.name:
        series.name = str(series.dtype)
    return pandas_dataframe_to_html(series.to_frame())


def register_pandas_formatter(formatters):  # pragma: no cover
    try:
        import pandas as pd
    except ImportError:
        pass
    else:
        pd.options.display.max_colwidth = 0
        formatters["text/html"].for_type(pd.DataFrame, pandas_dataframe_to_html)
        formatters["text/html"].for_type(pd.Series, pandas_series_to_html)


def sympy_extra_resources() -> Dict[str, List[str]]:
    js = (
        '<script type="text/x-mathjax-config">MathJax.Hub.Config({\n'
        'TeX: { equationNumbers: { autoNumber: "AMS" } } });</script>\n'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/'
        '2.7.0/MathJax.js?config=TeX-MML-AM_CHTML" defer></script>\n'
    )

    return {"extra_raw_javascript": [js]}


def register_sympy_formatter(formatters, latex_printer=None):  # pragma: no cover
    try:
        from sympy.core.basic import Basic
        from sympy.matrices.matrices import MatrixBase
        from sympy.physics.vector import Vector, Dyadic
        from sympy.tensor.array import NDimArray
    except ImportError:
        return

    from sympy import latex
    latex = latex_printer or latex

    def sympy_to_latex(obj) -> Tuple[str, Dict]:
        """Convert a Sympy's object into latex string."""
        return latex(obj, **formatter_kwargs), {"module": "sympy"}

    types = [Basic, MatrixBase, Vector, Dyadic, NDimArray]
    for cls in types:
        formatters["text/latex"].for_type(cls, sympy_to_latex)


def bokeh_to_html(obj) -> Tuple[str, Dict]:
    """Convert a Bokeh's obj into <script> and <div> tags."""
    from bokeh.embed import components

    script, div = components(obj)
    return script + div, {"module": "bokeh"}


def bokeh_extra_resources() -> Dict[str, List[str]]:
    from bokeh.resources import CDN

    return {"extra_css": CDN.css_files, "extra_javascript": CDN.js_files}


def register_bokeh_formatter(formatters):  # pragma: no cover
    try:
        from bokeh.plotting.figure import Figure
    except ImportError:
        pass
    else:
        formatters["text/html"].for_type(Figure, bokeh_to_html)


def holoviews_to_html(obj) -> Tuple[str, Dict]:
    import holoviews as hv

    renderer = hv.renderer("bokeh")
    try:
        html = renderer.html(obj, fmt=None)  # fmt=None is important!
    except ValueError:
        raise
    return html, {"module": "holoviews"}


def holoviews_extra_resources() -> Dict[str, List[str]]:
    import holoviews as hv

    renderer = hv.renderer("bokeh")
    js_html, css_html = renderer.html_assets()

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

    return _split_html_assets(js_html, css_html)


def register_holoviews_formatter(formatters):  # pragma: no cover
    try:
        from holoviews import Element, HoloMap
    except ImportError:
        pass
    else:
        for cls in [Element, HoloMap]:
            formatters["text/html"].for_type(cls, holoviews_to_html)


HTML_TEMPLATE = jinja2.Template(
    """<div id="{{ output_div }}"><script>
  document.addEventListener("DOMContentLoaded", function(event) {
    var spec = {{ spec }};
    var opt = {
      "mode": "vega-lite",
      "renderer": "canvas",
      "actions": {"editor": true, "source": true, "export": true}
    };
    vegaEmbed("#{{ output_div }}", spec, opt).catch(console.err);
  });</script></div>
"""
)


altair_counter = 0


def altair_to_html(obj) -> Tuple[str, Dict]:
    global altair_counter
    altair_counter += 1
    output_div = f"pheasant-altair-{altair_counter}"
    spec = json.dumps(obj.to_dict())
    html = HTML_TEMPLATE.render(output_div=output_div, spec=spec)
    return html, {"module": "altair"}


def altair_extra_resources() -> Dict[str, List[str]]:
    try:
        from altair.vegalite.v3.display import (
            VEGA_VERSION,
            VEGAEMBED_VERSION,
            VEGALITE_VERSION,
        )
    except ImportError:
        from altair.vegalite.v2.display import (  # type: ignore
            VEGA_VERSION,
            VEGAEMBED_VERSION,
            VEGALITE_VERSION,
        )

    BASE_URL = "https://cdn.jsdelivr.net/npm/"

    extra_raw_css = [
        "<style>\n .vega-actions a { margin-right: 12px; color: #757575; "
        "font-weight: normal; font-size: 13px; } .error { color: red; } </style>"
    ]

    extra_javascript = [
        f"{BASE_URL}vega@{VEGA_VERSION}",
        f"{BASE_URL}vega-lite@{VEGALITE_VERSION}",
        f"{BASE_URL}vega-embed@{VEGAEMBED_VERSION}",
    ]

    return {"extra_raw_css": extra_raw_css, "extra_javascript": extra_javascript}


def register_altair_formatter(formatters):  # pragma: no cover
    try:
        import altair as alt
    except ImportError:  # pragma: no cover
        pass
    else:
        types = [
            alt.Chart,
            alt.LayerChart,
            alt.HConcatChart,
            alt.VConcatChart,
            alt.FacetChart,
            alt.RepeatChart,
        ]
        for cls in types:
            formatters["text/html"].for_type(cls, altair_to_html)


def register_formatters(latex_printer=None):  # pragma: no cover
    ip = get_ipython()
    formatters = ip.display_formatter.formatters
    register_altair_formatter(formatters)
    register_bokeh_formatter(formatters)
    register_holoviews_formatter(formatters)
    register_sympy_formatter(formatters, latex_printer=latex_printer)
    register_pandas_formatter(formatters)


EXTRA_MODULES = ["altair", "bokeh", "holoviews", "sympy"]  # order is important


def get_extra_module(outputs: List[dict]) -> str:
    for output in outputs:
        if "metadata" in output:
            for key in ["text/html", "text/latex"]:
                module = output["metadata"].get(key, {}).get("module")
                if module in EXTRA_MODULES:
                    return module
    return ""


def _extra_resources(module: str) -> Dict[str, List[str]]:
    module_dict = {
        "bokeh": bokeh_extra_resources,
        "holoviews": holoviews_extra_resources,
        "altair": altair_extra_resources,
        "sympy": sympy_extra_resources,
    }
    return module_dict[module]()


def extra_resources(modules: Iterable[str]) -> Dict[str, List[str]]:
    keys = ["extra_" + x for x in ["css", "javascript", "raw_css", "raw_javascript"]]
    extra: Dict[str, List[str]] = {key: [] for key in keys}
    for module in EXTRA_MODULES:  # order is important
        if module in modules:
            data = _extra_resources(module)
            for key in data:
                for item in data[key]:
                    if item not in extra[key]:
                        extra[key].append(item)
    return extra


def _extra_html(extra: Dict[str, List[str]]) -> str:
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


def extra_html(modules: Iterable[str]) -> str:
    return _extra_html(extra_resources(modules))


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
    "image/gif",
    "text/plain",
]


def select_display_data(outputs: List[Dict]) -> None:
    """Select display data with the highest priority."""
    for output in outputs:
        for data_type in DISPLAY_DATA_PRIORITY:
            if "data" in output and data_type in output["data"]:
                output["data"] = {data_type: output["data"][data_type]}
                break


def select_last_display_data(outputs: List[Dict]) -> None:
    last = -1
    for k, output in enumerate(outputs):
        if output["type"] == "display_data":
            last = k
    if last == -1:
        return

    outputs[:] = [
        output for output in outputs[:last] if output["type"] != "display_data"
    ] + outputs[last:]

    join_stream(outputs)


def join_stream(outputs: List[Dict]) -> None:
    stream: Dict[str, List[str]] = {"stdout": [], "stderr": []}
    outputs_ = []
    for output in outputs:
        if output["type"] == "stream":
            stream[output["name"]].append(output["text"])
        else:
            outputs_.append(output)
    for name in ["stdout", "stderr"]:
        if stream[name]:
            text = "\n".join(stream[name])
            outputs_.append({"type": "stream", "name": name, "text": text})
    outputs[:] = outputs_


def select_outputs(outputs: List[Dict]) -> None:
    for output in outputs:
        if output["type"] == "display_data":
            outputs[:] = [
                output for output in outputs if output["type"] == "display_data"
            ]
        elif "data" in output and "text/plain" in output["data"]:
            text = output["data"]["text/plain"]
            if (text.startswith('"') and text.endswith('"')) or (
                text.startswith("'") and text.endswith("'")
            ):
                output["data"]["text/plain"] = ast.literal_eval(text)


def latex_display_format(outputs: List[Dict]) -> None:
    for output in outputs:
        if "data" in output and "text/latex" in output["data"]:
            text = output["data"]["text/latex"]
            output["data"]["text/latex"] = f"$${text}$$"

from altair.vegalite.v2.display import VEGALITE_VERSION, VEGAEMBED_VERSION, VEGA_VERSION
import jinja2

BASE_URL = "https://cdn.jsdelivr.net/npm/"

extra_raw_css = [
    "<style>\n .vega-actions a { margin-right: 12px; color: #757575; "
    "font-weight: normal; font-size: 13px; } .error { color: red; } </style>"
]

extra_javascript = [
    f"{BASE_URL}/vega@{VEGA_VERSION}",
    f"{BASE_URL}/vega-lite@{VEGALITE_VERSION}",
    f"{BASE_URL}/vega-embed@{VEGAEMBED_VERSION}",
]

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


counter = 0


def to_html(obj):
    global counter
    counter += 1
    output_div = f"pheasant-altair-{counter}"
    spec = obj.to_dict()
    return HTML_TEMPLATE.render(output_div=output_div, spec=spec)

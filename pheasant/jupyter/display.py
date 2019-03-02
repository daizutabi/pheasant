"""
A module processes inline code.

IMPORTANT: `display` function is called from jupyter kernel.
"""
import base64
import html
import io
import re
from typing import Any, Callable, Dict, Optional, Tuple, Union

from pheasant.jupyter.config import config
from pheasant.jupyter.renderer import delete_style
from pheasant.markdown.converter import markdown_convert

# type for output and its resources
Str_And_Dict = Tuple[str, Dict[str, list]]


def matplotlib_to_base64(obj, fmt: Optional[str] = None,
                         output: str = 'markdown') -> str:
    """Convert a Matplotlib's figure into base64 string."""
    if not hasattr(obj, 'savefig'):
        obj = obj.figure  # obj is axes.
    if fmt is None:
        fmt = config['matplotlib_format']

    buffer = io.BytesIO()
    obj.savefig(buffer, fmt=fmt, bbox_inches='tight', transparent=True)
    buffer.seek(0)
    binary = buffer.getvalue()
    buffer.close()

    return base64image(binary, fmt, output)


def base64image(binary: bytes, fmt: str, output: str) -> str:
    """Return markdown or HTML image source."""
    data = base64.b64encode(binary).decode('utf8')
    data = f'data:image/{fmt};base64,{data}'

    if output == 'markdown':
        return f'![{fmt}]({data})'
    elif output == 'html':
        return f'<img alt="{fmt}" src="{data}"/>'
    else:
        raise ValueError(f'Unknown output: {output}')


def pandas_to_html(dataframe, **kwargs) -> str:
    """Convert a pandas.DataFrame into a <table> tag."""
    html = dataframe.to_html(escape=False)
    html = delete_style(html)
    return html


def sympy_to_latex(obj, **kwargs) -> str:
    """Convert a Sympy's object into latex string."""
    import sympy
    return sympy.latex(obj)


def bokeh_to_html(obj, **kwargs) -> Str_And_Dict:
    """Convert a Bokeh's obj into <script> and <div> tags."""
    from bokeh.embed import components
    from bokeh.resources import CDN

    script, div = components(obj)
    resources = {'extra_css': CDN.css_files, 'extra_javascript': CDN.js_files}

    return script + div, resources


def holoviews_to_html(obj, output: str = 'markdown',
                      fmt: Optional[str] = None) -> Union[str, Str_And_Dict]:
    import holoviews as hv

    backend = config['holoviews_backend']
    if fmt is None:
        fmt = config[f'{backend}_format']

    renderer = hv.renderer(backend)

    if fmt == 'png':
        png, info = renderer(obj, fmt=fmt)
        return base64image(png, fmt, output)
    else:
        # html = renderer.html(obj, fmt)
        html = renderer.html(obj)
        js_html, css_html = renderer.html_assets()
        resources = _split_html_assets(js_html, css_html)
        return html, resources


def _split_html_assets(js_html: str, css_html: str) -> Dict[str, list]:
    resources = _split_js_html_assets(js_html)
    resources.update(_split_css_html_assets(css_html))
    return resources


def _split_js_html_assets(js_html: str) -> Dict[str, list]:
    pattern = r'<script src="(.*?)" type="text/javascript"></script>'
    extra_javascript = re.findall(pattern, js_html)

    pattern = r'<script type="text/javascript">(.*?)</script>'
    extra_raw_javascript = re.findall(pattern, js_html, re.DOTALL)

    return {'extra_javascript': extra_javascript,
            'extra_raw_javascript': extra_raw_javascript}


def _split_css_html_assets(css_html: str) -> Dict[str, list]:
    pattern = r'<link rel="stylesheet" href="(.*?)">'
    extra_css = re.findall(pattern, css_html)

    pattern = r'<style>(.*?)</style>'
    extra_raw_css = re.findall(pattern, css_html, re.DOTALL)

    return {'extra_css': extra_css,
            'extra_raw_css': extra_raw_css}


CONVERTERS: Dict[str, Callable] = {
    'matplotlib': matplotlib_to_base64, 'pandas': pandas_to_html,
    'sympy': sympy_to_latex, 'bokeh': bokeh_to_html,
    'holoviews': holoviews_to_html}


def display(obj: Any, **kwargs: Any) -> Union[str, Str_And_Dict]:
    if not hasattr(obj, '__module__'):
        is_str = isinstance(obj, str)
        if not is_str:
            obj = str(obj)

        if 'html' == kwargs.get('output'):
            return markdown_convert(obj)
        elif is_str:
            return obj
        else:
            return html.escape(obj)

    module = obj.__module__.split('.')[0]
    converter = CONVERTERS.get(module, lambda obj: str(obj))
    return converter(obj, **kwargs)

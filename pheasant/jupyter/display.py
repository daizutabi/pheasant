"""A module processes inline code."""
import base64
import html
import io
from typing import Any

from pheasant.jupyter.config import config
from pheasant.jupyter.renderer import delete_style
from pheasant.markdown.converter import markdown_convert


def display(obj: Any, **kwargs: Any) -> str:
    # FIXME: how to determine the function for conversion.
    if hasattr(obj, '__module__'):
        module = obj.__module__
        if module.startswith('matplotlib.'):
            source = matplotlib_to_base64(obj, **kwargs)
        elif module.startswith('pandas.'):
            source = pandas_to_html(obj)
        elif module.startswith('bokeh.'):
            source = bokeh_to_html(obj)
        elif module.startswith('holoviews.'):
            source = holoviews_to_html(obj)
        elif module.startswith('sympy.'):
            source = sympy_to_latex(obj)
        else:
            source = str(obj)
    else:
        is_str = isinstance(obj, str)
        if not is_str:
            obj = str(obj)

        if 'html' == kwargs.get('output'):
            source = markdown_convert(obj)
        elif is_str:
            source = obj
        else:
            source = html.escape(obj)

    return source


def to_html(obj: Any, **kwargs: Any) -> str:
    return display(obj, output='html')


def to_markdown(obj: Any, **kwargs: Any) -> str:
    return display(obj, output='markdown')


def pandas_to_html(dataframe) -> str:
    """Convert a pandas.DataFrame into a <table> tag."""
    html = dataframe.to_html(escape=False)
    html = delete_style(html)
    return html


def bokeh_to_html(figure) -> str:
    """Convert a Bokeh's figure into <script> and <div> tags."""
    from bokeh.embed import components
    script, div = components(figure)
    return script + div


def sympy_to_latex(obj) -> str:
    """Convert a Sympy's object into latex string."""
    import sympy as sp
    return sp.latex(obj)


def matplotlib_to_base64(obj, output='markdown') -> str:
    """Convert a Matplotlib's figure into base64 string."""
    format = config['matplotlib_format']
    buf = io.BytesIO()

    if not hasattr(obj, 'savefig'):
        obj = obj.figure  # obj is axes.

    obj.savefig(buf, format=format, bbox_inches='tight', transparent=True)
    buf.seek(0)
    binary = buf.getvalue()

    return base64image(binary, format, output)


def holoviews_to_html(figure, output='markdown') -> str:
    import holoviews as hv
    backend = config['holoviews_backend']
    format = config[f'{backend}_format']
    renderer = hv.renderer(backend)
    html, info = renderer(figure, fmt=format)

    if format == 'png':
        return base64image(html, format, output)
    else:
        return html


def base64image(binary, format: str, output: str) -> str:
    data = base64.b64encode(binary).decode('utf8')
    data = f'data:image/{format};base64,{data}'

    if output == 'markdown':
        return f'![{format}]({data})'
    elif output == 'html':
        return f'<img alt="{format}" src="{data}"/>'
    else:
        raise ValueError(f'Unknown output: {output}')

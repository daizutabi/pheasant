"""This module processes inline code."""

import base64
import html
import io

from ..markdown.convert import markdown_convert


def convert_inline(obj, **kwargs):
    # FIXME: how to determine the function for conversion.
    if hasattr(obj, '__module__'):
        module = obj.__module__
        if module.startswith('matplotlib.'):
            return to_base64(obj, **kwargs)
        elif module.startswith('pandas.'):
            return to_html(obj)
        elif module.startswith('bokeh.'):
            return to_script_and_div(obj)
    else:
        is_str = isinstance(obj, str)
        if not is_str:
            obj = str(obj)

        if 'html' == kwargs.get('output'):
            return markdown_convert(obj)
        elif is_str:
            return obj
        else:
            return html.escape(obj)


def to_html(df):
    """Convert a pandas.DataFrame into a <table> tag."""
    # from IPython.display import HTML
    # return HTML(df.to_html(escape=False))
    return df.to_html(escape=False)


def to_script_and_div(fig):
    """Convert a Bokeh's figure into <script> and <div> tags."""
    from bokeh.embed import components
    script, div = components(fig)
    return script + div


def to_base64(obj, format='png', output='markdown'):
    """Convert a Matplotlib's figure into base64 string."""
    buf = io.BytesIO()

    if not hasattr(obj, 'savefig'):
        obj = obj.figure  # obj is axes.

    obj.savefig(buf, format=format, bbox_inches='tight', transparent=True)
    buf.seek(0)

    data = base64.b64encode(buf.getvalue()).decode('utf8')
    data = f'data:image/{format};base64,{data}'

    if output == 'markdown':
        return f'![{format}]({data})'
    elif output == 'html':
        return f'<img alt="{format}" src="{data}"/>'

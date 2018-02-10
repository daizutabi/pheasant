"""This module processes inline code."""

import base64
import html
import io

from markdown import Markdown

from .config import config

extensions = ['tables', 'fenced_code']
md = Markdown(extensions=extensions + config['markdown_extensions'])


def convert_inline(obj, **kwargs):
    if not hasattr(obj, '__module__'):
        obj = str(obj)
        if 'html' == kwargs.get('output'):
            return md.convert(obj)
        else:
            return html.escape(obj)

    # FIXME: how to determine the function for conversion.
    module = obj.__module__
    if module.startswith('matplotlib.'):
        return to_base64(obj, **kwargs)
    elif module.startswith('pandas.'):
        return to_html(obj)
    elif module.startswith('bokeh.'):
        return to_script_and_div(obj)


def to_html(df):
    from IPython.display import HTML
    return HTML(df.to_html(escape=False))


def to_script_and_div(fig):
    from bokeh.embed import components
    script, div = components(fig)
    return script + div


def to_base64(fig, format='png', output='markdown'):
    """Convert a Matplotlib's figure into base64 string."""
    buf = io.BytesIO()

    if not hasattr(fig, 'savefig'):
        fig = fig.figure  # fig is axes.

    fig.savefig(buf, format=format, bbox_inches='tight', transparent=True)
    buf.seek(0)

    data = base64.b64encode(buf.getvalue()).decode('utf8')
    data = f'data:image/{format};base64,{data}'

    if output == 'markdown':
        return f'![{format}]({data})'
    elif output == 'html':
        return f'<img alt="{format}" src="{data}" />'


# def preprocess_markdown(source: str) -> str:
#     extensions = ['tables', 'fenced_code']
#     md = Markdown(extensions=extensions + config['markdown_extensions'])
#
#     def replace(m):
#         code = m.group(1)
#
#         if code.startswith(config['inline_ignore_character']):
#             return m.group().replace(code, code[1:])
#
#         to_html = code.startswith(config['inline_html_character'])
#         if to_html:
#             code = code[1:]
#
#         cell = nbformat.v4.new_code_cell(code.strip())
#
#         markdown = run_and_export(cell, inline_export)
#
#         if to_html:
#             return md.convert(markdown)
#         else:
#             return markdown
#
#     return re.sub(config['inline_pattern'], replace, source)

"""This module processes inline code."""

import base64
import io

from IPython.display import HTML


def convert_inline(obj, **kwargs):
    import pandas as pd
    from bokeh.plotting.figure import Figure
    print(obj)

    if isinstance(obj, pd.DataFrame):
        return to_html(obj)
    elif isinstance(obj, Figure):
        return to_script_and_div(obj)
    else:
        return to_base64(obj, **kwargs)


def to_html(df):
    return HTML(df.to_html(escape=False))


def to_script_and_div(fig):
    print('here')
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

import html


def set_config(config):
    from .jupyter import set_config
    return set_config(config['jupyter'])


def convert(source):
    from .jupyter import convert
    source = convert(source)
    if not isinstance(source, str):
        source = html.escape(str(source))
        source = f'<h1>DEBUG MODE</h1><pre>{source}</pre>'
    return source

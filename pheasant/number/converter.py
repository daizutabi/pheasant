from .config import config
from .markdown import convert as convert_markdown


def convert(source):
    from ..converters import get_source_file
    source_file = get_source_file()
    if source_file not in config['pages']:
        config['pages'].append(source_file)

    index = config['pages'].index(source_file)

    source = convert_markdown(source, index)

    return source

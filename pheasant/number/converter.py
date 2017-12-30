import logging

from .config import config
from .header import convert as convert_header

logger = logging.getLogger(__name__)


def convert(source):
    from ..converters import get_source_file
    source_file = get_source_file()
    if source_file not in config['pages']:
        config['pages'].append(source_file)

    page_index = [config['pages'].index(source_file) + 1]
    logger.info(f'Page index for {source_file}: {page_index}')

    source, tag_dictionary = convert_header(source, page_index)

    return source

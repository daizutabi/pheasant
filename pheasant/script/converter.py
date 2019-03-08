import re
from typing import Iterator

from pheasant.script.config import config
from pheasant.script.formatter import Formatter
from pheasant.script.splitter import cell_splitter


def initialize():
    if config['option_pattern']:
        Formatter.OPTION_PATTERN = re.compile(
            config['option_pattern'], re.MULTILINE)
    if config['option_pattern']:
        Formatter.COMMENT_PATTERN = re.compile(
            config['comment_pattern'], re.MULTILINE)


def convert(source: str) -> str:
    from pheasant.converters import get_source_file
    source_file = get_source_file()

    if source_file is None or source_file.endswith('.py'):
        return '\n'.join(cell_formatter(source))
    else:
        return source


def cell_formatter(source: str) -> Iterator[str]:
    formatter = Formatter(source)

    for cell_type, begin, end in cell_splitter(source):
        yield formatter(cell_type, begin, end)

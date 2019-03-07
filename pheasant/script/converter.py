import re
from typing import Generator

from pheasant.script.config import config, Cell
from pheasant.script.splitter import cell_splitter


def initialize():
    config['OPTIONS_PATTERN'] = re.compile(config['option_pattern'],
                                           re.MULTILINE)
    config['SEPARATOR_PATTERN'] = re.compile(config['separator_pattern'])
    config['COMMENT_PATTERN'] = re.compile(config['comment_pattern'],
                                           re.MULTILINE)


def convert(source: str) -> str:
    from pheasant.converters import get_source_file
    source_file = get_source_file()

    if source_file is None or source_file.endswith('.py'):
        return '\n'.join(cell_generator(source))
    else:
        return source


def cell_generator(source: str) -> Generator[str, None, None]:
    for cell_type, content in cell_splitter(source):
        if cell_type == Cell.MARKDOWN:
            yield re.sub(config['COMMENT_PATTERN'], '', content)
        else:
            match = re.match(config['OPTION_PATTERN'], content)
            if match:
                options = match.group(2)
                content = content.replace(match.group(1) + match.group(2), '')
                options = ' ' + options
            else:
                options = ''
            yield f'```python{options}\n{content}```\n'

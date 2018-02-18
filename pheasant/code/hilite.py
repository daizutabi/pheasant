import re


from ..markdown.converter import fenced_code_convert
from ..markdown.splitter import splitter
from ..number import config as config_number


def convert(source: str):
    source = ''.join(render(source))
    return source


def render(source: str):
    """Yield formatted fenced code and other normal part."""
    pattern = r'(```(.*?)```)|(~~~(.*?)~~~)'
    re_option = re.DOTALL | re.MULTILINE
    for splitted in splitter(pattern, source, option=re_option):
        if isinstance(splitted, str):
            yield splitted
        else:
            source = splitted.group(2) or splitted.group(4)
            source = f'```{source}\n```'
            yield format_source(source)


def format_source(source: str) -> str:
    """Highlight the source and add classes, begin, and end statements."""
    source = fenced_code_convert(source, only_code=True)
    cls = 'pheasant-markdown pheasant-code'
    content = f'<div class="codehilite {cls}"><pre>{source}</pre></div>'
    begin = config_number['begin_pattern']
    end = config_number['end_pattern']
    return f'{begin}\n{content}\n{end}'

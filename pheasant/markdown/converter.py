import re
from typing import Optional

from markdown import Markdown

markdown_converter = Markdown(extensions=['fenced_code', 'tables'])

CLASS = '__CLASS'

fenced_code_converter = Markdown(
    extensions=['fenced_code', 'codehilite'],
    extension_configs={'codehilite': {
        'css_class': CLASS
    }})


def markdown_convert(source: str, extensions: Optional[str] = None) -> str:
    if extensions is None:
        return markdown_converter.convert(source)
    else:
        converter = Markdown(extensions=extensions)
        return converter.convert(source)


pre_pattern = re.compile(r'.*?<pre>(.*?)</pre>', flags=re.DOTALL)


def fenced_code_convert(source: str,
                        cls: str = 'codehilite',
                        only_code: bool = False) -> str:
    source = fenced_code_converter.convert(source)
    source = source.replace(CLASS, cls)
    if only_code:
        match = pre_pattern.match(source)
        source = match.group(1) if match else ''
    return source

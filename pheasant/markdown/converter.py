from typing import Optional

from markdown import Markdown

markdown_converter = Markdown(extensions=['fenced_code', 'tables'])


def markdown_convert(source: str, extensions: Optional[str] = None) -> str:
    if extensions is None:
        return markdown_converter.convert(source)
    else:
        converter = Markdown(extensions=extensions)
        return converter.convert(source)

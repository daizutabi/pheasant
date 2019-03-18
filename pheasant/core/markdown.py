from typing import List, Optional

from markdown import Markdown

markdown = Markdown(extensions=["tables"])


def convert(source: str, extensions: Optional[List[str]] = None) -> str:
    if extensions is None:
        return markdown.convert(source)
    else:
        markdown_ = Markdown(extensions=extensions)
        return markdown_.convert(source)

import re

from ..utils import escaped_splitter
from .config import config


def convert(source: str, tag: dict):
    return ''.join(renderer(source, tag))


def renderer(source: str, tag: dict):
    """
    Generate splitted reference and body text from `source`.

    some text {ref}, another text

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    splitted source : str or dict
    """

    pattern_escape = r'(^```(.*?)^```$)|(^~~~(.*?)^~~~$)'
    pattern_tag = config['tag_pattern']

    for splitted in escaped_splitter(pattern_tag, pattern_escape, source):
        if isinstance(splitted, str):
            yield splitted
        else:
            entity = splitted.group(1)
            if entity in tag:
                yield config['template'].render(reference=True, config=config,
                                                **tag[entity])
            else:
                yield splitted.group()

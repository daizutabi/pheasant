import re

from ..utils import splitter
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

    pattern_fenced_code = r'(^```(.*?)^```$)|(~~~(.*?)^~~~)'
    option_fenced_code = re.DOTALL | re.MULTILINE

    for splitted in splitter(pattern_fenced_code, source, option_fenced_code):
        if not isinstance(splitted, str):
            yield splitted.group().strip()
            continue
        for splitted in splitter(config['tag_pattern'], splitted):
            if isinstance(splitted, str):
                yield splitted
            else:
                entity = splitted.group(1)
                if entity in tag:
                    yield config['template'].render(reference=True,
                                                    config=config,
                                                    **tag[entity])
                else:
                    yield splitted.group()

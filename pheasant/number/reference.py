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
    for splitted in splitter(config['tag_pattern'], source):
        if isinstance(splitted, str):
            yield splitted
        else:
            entity = splitted.group(1)
            if entity in tag:
                yield config['template'].render(reference=True, **tag[entity],
                                                config=config)
            else:
                yield splitted.group()

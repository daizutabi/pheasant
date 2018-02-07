from ..utils import escaped_splitter
from .config import config


def convert(source: str, label: dict):
    return ''.join(renderer(source, label))


def renderer(source: str, label: dict):
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
    pattern_label = config['label_pattern']

    for splitted in escaped_splitter(pattern_label, pattern_escape, source):
        if isinstance(splitted, str):
            yield splitted
        else:
            entity = splitted.group(1)
            if entity in label:
                yield config['template'].render(reference=True, config=config,
                                                **label[entity])
            else:
                yield splitted.group()

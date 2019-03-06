from typing import Generator

from pheasant.markdown.splitter import escaped_splitter
from pheasant.number.config import config


def convert(source: str, label: dict) -> str:
    return ''.join(render(source, label))


def render(source: str, label: dict) -> Generator[str, None, None]:
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

    pattern_escape = r'(^```(.*?)^```$)|(^~~~(.*?)^~~~$)|(<pre>(.*?)</pre>)'
    pattern_label = config['label_pattern']

    for splitted in escaped_splitter(pattern_label, pattern_escape, source,
                                     escape_generator=None):
        if isinstance(splitted, tuple):
            pass  # Never occur. Just for mypy.
        elif isinstance(splitted, str):
            yield splitted
        else:
            entity = splitted.group(1)
            if entity in label:
                yield config['template'].render(reference=True, config=config,
                                                **label[entity])
            else:
                yield splitted.group()

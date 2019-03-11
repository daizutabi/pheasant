from typing import Iterator

from pheasant.markdown.splitter import escaped_splitter
from pheasant.number.config import config, ESCAPE_PATTEN


def convert(source: str, label: dict) -> str:
    return "".join(render(source, label))


def render(source: str, label: dict) -> Iterator[str]:
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

    # pattern_escape = r"(^```(.*?)^```$)|(^~~~(.*?)^~~~$)|(<pre>(.*?)</pre>)"
    pattern_label = config["LABEL_PATTERN"]

    for splitted in escaped_splitter(
        pattern_label, ESCAPE_PATTEN, source, escape_generator=None
    ):
        if isinstance(splitted, tuple):
            pass  # Never occur. Just for mypy.
        elif isinstance(splitted, str):
            yield splitted
        else:
            entity = splitted.group(1)
            if entity in label:
                yield config["template"].render(
                    reference=True, config=config, **label[entity]
                )
            else:
                yield splitted.group()

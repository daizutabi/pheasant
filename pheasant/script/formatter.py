import re
import unicodedata
from functools import reduce
from itertools import accumulate
from typing import Iterator

COMMENT_PATTERN = re.compile(r"^#\s*", re.MULTILINE)


def format_comment(source: str, max_line_length: int = 88) -> str:
    """Format a comment source to python code or markdown.

    Output format is determined by `max_line_length`:
        -1: Just remove `#` and following spaces at the beginning of each line.
         0: Markdown source formatted to one line.
        >1: Python script wrapped with the max line length.

    Any wide characters take two-character spaces to calculate the line length.

    Parameters
    ----------
    source
        Comment source to be formatted.
    max_line_length
        Preferred line length when source is formatted to a Python script.
        If 0, source is formatted to a Markdown source and its line length is
        not limitted.

    Returns
    -------
    output
        Formatted output.
    """
    source = COMMENT_PATTERN.sub("", source)
    if max_line_length == -1:
        return source
    else:
        return "\n".join(wrap(source, max_line_length)) + "\n"


def wrap(source: str, max_line_length: int, pre: str = "# ") -> Iterator[str]:
    line = join(source)
    if max_line_length == 0:
        yield line
        return

    max_line_length -= len(pre)
    if len(line) <= max_line_length:
        yield pre + line
        return

    is_wides = [is_wide(character) for character in line]
    distance = list(accumulate(2 if x else 1 for x in is_wides))
    splittable = [is_splittable(line, index) for index in range(1, len(line))]

    begin = end = cursor = 0
    while True:
        if splittable[cursor]:
            end = cursor
        cursor += 1
        if cursor == len(line) - 1:
            yield pre + line[begin:].strip()
            break
        elif distance[cursor] - distance[begin] >= max_line_length and begin != end:
            yield pre + line[begin : end + 1].strip()
            begin = end = end + 1


def is_wide(character: str) -> bool:
    return unicodedata.east_asian_width(character) in ["F", "W"]


def is_splittable(line: str, index: int) -> bool:
    return line[index] == " " or is_wide(line[index - 1]) or is_wide(line[index])


def join(source: str) -> str:
    def joint(tail: str, head: str) -> str:
        if is_wide(tail) and is_wide(head):
            return ""
        else:
            return " "

    def join(first: str, second: str) -> str:
        return joint(first[-1], second[0]).join([first, second])

    lines = source.split("\n")[:-1]
    return reduce(join, lines[1:], lines[0])

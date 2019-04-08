import unicodedata
from functools import reduce
from itertools import accumulate
from typing import Iterator


def format_source(source: str, max_line_length: int = 88) -> str:
    """Format a source to python code or markdown.

    Output format is determined by `max_line_length`:
         0: formatted to one line.
        >1: wrapped with the max line length.

    Any wide characters take two-character spaces to calculate the line length.

    Parameters
    ----------
    source
        Source to be formatted.
    max_line_length
        Preferred line length.
        If 0, the source is formatted to a one-line source and its line length is
        not limitted.

    Returns
    -------
    output
        Formatted output.
    """
    return "\n".join(wrap(source, max_line_length)) + "\n"


def wrap(source: str, max_line_length: int) -> Iterator[str]:
    line = join(source)

    is_wides = [is_wide(character) for character in line]
    distance = list(accumulate(2 if x else 1 for x in is_wides))
    if max_line_length <= 0 or distance[len(line) - 1] <= max_line_length:
        yield line
        return

    splittable = [is_splittable(line, index) for index in range(len(line))]

    begin = end = cursor = 0
    while True:
        if splittable[cursor]:
            end = cursor
        cursor += 1
        if cursor == len(line):
            yield line[begin:].strip()
            break
        elif distance[cursor] - distance[begin] >= max_line_length and begin != end:
            if line[cursor] == " ":
                end = cursor
            yield line[begin : end + 1].strip()
            begin = end = end + 1


def is_wide(character: str) -> bool:
    return unicodedata.east_asian_width(character) in ["F", "W"]


def is_splittable(line: str, index: int) -> bool:
    if index < len(line) - 1:
        return line[index] == " " or is_wide(line[index]) or is_wide(line[index + 1])
    else:
        return False


def join(source: str) -> str:
    def joint(tail: str, head: str) -> str:
        if is_wide(tail) or is_wide(head):
            return ""
        else:
            return " "

    def join(first: str, second: str) -> str:
        return joint(first[-1], second[0]).join([first, second])

    lines = source.split("\n")[:-1]
    return reduce(join, lines[1:], lines[0])

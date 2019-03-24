import unicodedata
from functools import reduce
from itertools import accumulate
from typing import Iterator

from pyls_cwrap.config import Line, _new_line_character
from pyls_cwrap.splitter import splitter


def format_text(source: str, max_line_length: int = 79) -> str:
    nl = _new_line_character(source)
    return nl.join(wrapper(source, max_line_length))


def wrapper(source: str, max_line_length: int) -> Iterator[str]:
    for kind, line in joiner(source):
        if kind == "Comment":
            yield from wrap(line, max_line_length)
        else:
            yield line


def wrap(line: str, max_line_length: int, pre: str = "# ") -> Iterator[str]:
    max_line_length -= len(pre)
    is_wides = [is_wide(x) for x in line]
    position = list(accumulate(2 if x else 1 for x in is_wides))
    splitterable = [False] + [
        x == " " or (is_wides[k] and is_wides[k + 1]) for k, x in enumerate(line[1:])
    ]

    begin = end = head = 0
    while True:
        if splitterable[head]:
            end = head
        head += 1
        if head >= len(line):
            yield pre + line[begin:].strip()
            break
        elif position[head] - position[begin] - 1 >= max_line_length and begin != end:
            yield pre + line[begin : end + 1].strip()
            begin = end = end + 1


def is_wide(character: str) -> bool:
    return unicodedata.east_asian_width(character) in ["F", "W"]


def is_splittable(line, head) -> bool:
    return line[head] == " " or is_wide(head - 1) or is_wide(head)


def joiner(source: str) -> Iterator[Line]:
    def joint(tail: str, head: str) -> str:
        if is_wide(tail) and is_wide(head):
            return ""
        else:
            return " "

    def join(first: str, second: str) -> str:
        return joint(first[-1], second[0]).join([first, second])

    iterator = splitter(source)
    for kind, line in iterator:
        if kind == "Comment":
            lines = []
            for kind, line_ in iterator:
                if kind == "Comment":
                    lines.append(line_)
                else:
                    yield "Comment", reduce(join, lines, line)
                    yield kind, line_
                    break
            else:
                yield "Comment", reduce(join, lines, line)
        else:
            yield kind, line

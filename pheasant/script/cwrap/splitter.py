import ast
import re
from itertools import repeat
from typing import Iterator, List

from pyls_cwrap.config import (AST_PATTERN, COMMENT_PATTERN, ESCAPE_PATTERN,
                               Line, _new_line_character)


def splitter(source: str) -> Iterator[Line]:
    iterator = source_splitter(source)
    for kind, line in iterator:
        if not line:
            yield "Code", ""
        elif kind == "Code":
            yield kind, line
        elif line.startswith("# #"):
            yield "Escape", line
        else:
            match = re.match(ESCAPE_PATTERN, line)
            if match:
                yield "Escape", line
                escape_pattern = match.group()
                for kind, line in iterator:
                    yield "Escape", line
                    if line.startswith(escape_pattern):
                        break
            else:
                line = re.sub(COMMENT_PATTERN, "", line)
                if line:  # Drop comment line without any text.
                    yield "Comment", line


def source_splitter(source: str) -> Iterator[Line]:
    nl = _new_line_character(source)
    node = ast.parse(source)
    names = [ast_name(obj) for obj in node.body]
    lines = source.split(nl)

    if not names:  # Comment only.
        yield from zip(repeat("Comment"), lines)
        return

    first_line_numbers = [obj.lineno - 1 for obj in node.body]  # 0-indexed
    last_line_numbers = [
        file_last_line_number(lines, no - 1)
        for no in first_line_numbers[1:] + [len(lines) - 1]
    ]

    if first_line_numbers[0] != 0:
        yield from zip(repeat("Comment"), lines[: first_line_numbers[0]])

    cursor = first_line_numbers[0]
    for name, first, last in zip(names, first_line_numbers, last_line_numbers):
        if cursor < first:
            yield from zip(repeat("Comment"), lines[cursor:first])
        cursor = last + 1
        yield "Code", nl.join(lines[first:cursor])
    if cursor <= len(lines) - 1:
        yield from zip(repeat("Comment"), lines[cursor:])


def ast_name(node: ast.AST) -> str:
    """Returns the node name."""
    match = re.match(AST_PATTERN, str(node))
    if match:
        return match.group(1)
    else:
        return "Unknown"


def file_last_line_number(lines: List[str], no: int) -> int:
    def is_code(line: str) -> bool:
        return len(line) > 0 and not line.startswith("#")

    while True:
        if is_code(lines[no]) or no == -1:
            return no
        else:
            no -= 1

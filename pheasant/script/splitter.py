import ast
import re
from typing import Iterator, List, Tuple

Element = Tuple[str, int, int]


def splitter(source: str) -> Iterator[Element]:
    splitter = source_splitter(source)
    for name, begin, end in splitter:
        if name == "Code":
            first = begin
            while name == "Code":
                last = end
                try:
                    name, begin, end = next(splitter)
                except StopIteration:
                    break
            yield "Code", first, last
            if name in ["Markdown", "Escape"]:
                yield name, begin, end
        else:
            yield name, begin, end


def source_splitter(source: str) -> Iterator[Element]:
    node = ast.parse(source)
    names = [ast_name(obj) for obj in node.body]
    lines = source.split("\n")

    if not names:  # Markdown only.
        yield from markdown_trimmer(lines, 0, len(lines) - 1)
        return

    first_line_numbers = [obj.lineno - 1 for obj in node.body]  # 0-indexed
    last_line_numbers = [
        file_last_line_number(lines, no - 1)
        for no in first_line_numbers[1:] + [len(lines) - 1]
    ]

    if first_line_numbers[0] != 0:
        yield from markdown_trimmer(lines, 0, first_line_numbers[0] - 1)
    cursor = first_line_numbers[0]
    for name, first, last in zip(names, first_line_numbers, last_line_numbers):
        if cursor < first:
            yield from markdown_trimmer(lines, cursor, first - 1)
        yield "Code", first, last
        cursor = last + 1
    if cursor <= len(lines) - 1:
        yield from markdown_trimmer(lines, cursor, len(lines) - 1)


SEPARATOR = "# -"


def markdown_trimmer(lines: List[str], first: int, last: int) -> Iterator[Element]:
    begin = end = -1
    for cursor in range(first, last + 1):
        if lines[cursor]:
            if begin == -1:
                begin = cursor
            end = cursor
    if begin != -1:
        if begin == end and lines[begin].startswith(SEPARATOR):
            yield "Separator", begin, end
        else:
            yield from escape_splitter(lines, begin, end)


ESCAPE_PATTERN = re.compile(r"^# (~{3,}|`{3,})")


def escape_splitter(lines: List[str], first: int, last: int) -> Iterator[Element]:
    begin = first
    in_escape = False
    escape_prefix = ""
    for cursor in range(first, last + 1):
        match = re.match(ESCAPE_PATTERN, lines[cursor])
        if match and (not in_escape or match.group() == escape_prefix):
            if in_escape:
                yield "Escape", begin, cursor
                begin = cursor + 1
            else:
                yield "Markdown", begin, cursor - 1
                begin = cursor
                escape_prefix = match.group()
            in_escape = not in_escape

    yield "Escape" if in_escape else "Markdown", begin, cursor


AST_PATTERN = re.compile(r"<_ast\.(.+?) ")


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

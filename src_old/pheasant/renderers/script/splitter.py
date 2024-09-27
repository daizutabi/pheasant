import ast
import re
from typing import Iterator, List, Tuple

pattern = r'^(?P<quote>"""|\'\'\')(.*?)(?P=quote)\n'
DOCSTRING_PATTERN = re.compile(pattern, re.DOTALL | re.MULTILINE)
AST_PATTERN = re.compile(r"<_ast\.(.+?) ")
CELL_PATTERN = re.compile(r"^# %%.*?\n", re.MULTILINE)


def split(source: str) -> Iterator[Tuple[str, str]]:
    cursor = 0
    for match in DOCSTRING_PATTERN.finditer(source):
        start, end = match.start(), match.end()
        if cursor < start:
            yield from split_block(source[cursor:start])
        yield "Docstring", match.group()
        cursor = end
    if cursor < len(source):
        yield from split_block(source[cursor:])


def split_block(source: str) -> Iterator[Tuple[str, str]]:
    if CELL_PATTERN.search(source):
        yield from split_block_from_cell(source)
    else:
        yield from split_block_from_line(source)


def split_block_from_cell(source: str) -> Iterator[Tuple[str, str]]:
    kind = ""
    start = 0
    for match in CELL_PATTERN.finditer(source):
        if start:
            if kind == "Comment":
                yield from split_block_from_line(source[start : match.start()])
            else:
                yield kind, source[start : match.start()]
        yield "Cell", match.group()
        start = match.end()
        kind = "Comment" if "markdown" in match.group() else "Code"
    if kind == "Comment":
        yield from split_block_from_line(source[start:])
    else:
        yield kind, source[start:]


def split_block_from_line(source) -> Iterator[Tuple[str, str]]:
    current = ""
    lines = []
    for kind, line in split_line(source):
        if current in ["Comment", "Blank"]:
            if kind == current:
                lines.append(line)
            elif (
                kind == "Code"
                and current == "Comment"
                and not lines[-1].startswith("# -")
            ):
                lines.append(line)
                current = "Code"
            else:
                yield current, "\n".join(lines) + "\n"
                current = kind
                lines = [line]
        elif current == "Code":
            if kind != "Comment":
                lines.append(line)
            else:
                for k, line_ in enumerate(reversed(lines)):
                    if line_:
                        break
                yield current, "\n".join(lines[: len(lines) - k]) + "\n"
                if k:
                    yield "Blank", "\n".join(lines[len(lines) - k :]) + "\n"
                current = kind
                lines = [line]
        else:
            current = kind
            lines = [line]
    yield current, "\n".join(lines) + "\n"


def split_line(source: str) -> Iterator[Tuple[str, str]]:
    if not source.endswith("\n"):
        source = source + "\n"
    lines = source.split("\n")[:-1]
    node = ast.parse(source)
    names = [ast_name(obj) for obj in node.body]  # type: ignore

    def commentiter(lines):
        for line in lines:
            if line:
                kind = "Comment"
            else:
                kind = "Blank"
            yield kind, line

    if not names:  # Comment only.
        yield from commentiter(lines)
        return

    begin_linenos = [obj.lineno - 1 for obj in node.body]  # type: ignore
    linenos = begin_linenos[1:] + [len(lines)]
    end_linenos = [find_end_line(lines, lineno) for lineno in linenos]

    cursor = begin_linenos[0]
    if cursor != 0:
        yield from commentiter(lines[:cursor])

    for name, begin, end in zip(names, begin_linenos, end_linenos):
        if cursor < begin:
            yield from commentiter(lines[cursor:begin])
        yield "Code", "\n".join(lines[begin:end])
        cursor = end
    if cursor < len(lines):
        yield from commentiter(lines[cursor:])


def ast_name(node: ast.AST) -> str:
    """Returns the node name."""
    match = re.match(AST_PATTERN, str(node))
    if match:
        return match.group(1)
    else:
        return "Unknown"  # pragma: no cover


def find_end_line(lines: List[str], lineno: int) -> int:
    def is_code(line: str) -> bool:
        return len(line) > 0 and not line.startswith("#")

    while True:
        if is_code(lines[lineno - 1]) or lineno == 0:
            return lineno
        else:
            lineno -= 1

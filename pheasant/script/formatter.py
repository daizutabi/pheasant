"""Format Python commnet and code for suitable format as Markdown"""

import re
import unicodedata
from itertools import chain
from typing import Iterator, Pattern, List


class Formatter:
    OPTION_PATTERN: Pattern = re.compile(r".*?(\s{2,}# -)(.+)$", re.MULTILINE)
    COMMENT_PATTERN: Pattern = re.compile(r"^# ", re.MULTILINE)

    def __init__(self, source: str):
        self.lines = source.split("\n")
        self.language = "python"

    def __len__(self):
        return len(self.lines)

    def __call__(self, cell_type: str, begin: int, end: int) -> str:
        return self.format_(cell_type, begin, end)

    def content(self, begin: int, end: int):
        """Join the lines and add a new line at the end."""
        return "\n".join(self.lines[begin : end + 1]) + "\n"

    def format_(self, cell_type: str, begin: int, end: int) -> str:
        """Format `str` lines according to the cell type.

        Parameters
        ----------
        cell_type : 'Markdown' or 'Code'
        begin, end : 0-indexed line number at which cell starts and ends.

        Returns
        -------
        cell_content : Formatted cell content.
         """

        if cell_type == "Markdown":
            return self.markdown(begin, end)
        else:
            return self.code(begin, end)

    def markdown(self, begin: int, end: int) -> str:
        body = [
            re.sub(self.COMMENT_PATTERN, "", line)
            for line in self.lines[begin : end + 1]
        ]
        joiner = markdown_joiner(body)
        return "".join(chain(*zip(body, joiner)))

    def code(self, begin, end):
        source = self.content(begin, end)
        match = re.match(self.OPTION_PATTERN, source)
        if match:
            options = match.group(2)
            source = source.replace(match.group(1) + match.group(2), "")
            options = " " + options
        else:
            options = ""
        source = re.sub("\n{3,}", "\n\n", source)  # for saving spaces.
        return f"```{self.language}{options}\n{source}```\n"


def is_wide(character):
    return unicodedata.east_asian_width(character) in ["F", "W"]


def markdown_joiner(lines: List[str]) -> Iterator[str]:
    for cur in range(len(lines) - 1):
        if not lines[cur]:
            yield "\n"
        else:
            tail = lines[cur][-1]
            if not lines[cur + 1]:
                yield "\n"
            else:
                head = lines[cur + 1][0]
                if is_wide(tail) and is_wide(head):
                    yield ""
                else:
                    yield " "
    yield "\n"

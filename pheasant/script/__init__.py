import re
from typing import Tuple

AST_PATTERN = re.compile(r"<_ast\.(.+?) ")
COMMENT_PATTERN = re.compile(r"^#\s*")
ESCAPE_PATTERN = re.compile(r"^#\s*(~{3,}|`{3,})")
HEADER_PATTERN = re.compile(r"^#\s*#")


def _new_line_character(source):
    """Returns the new line code according to the current source."""
    return "\r\n" if "\r\n" in source else "\n"


Line = Tuple[str, str]

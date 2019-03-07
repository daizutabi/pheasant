from typing import Any, Dict
from enum import Enum

config: Dict[str, Any] = {
    # Option pattern.
    'option_pattern': r'.*?(\s{2,}# -)(.+)$',

    # Separator pattern.
    'separator_pattern': r'^# -',

    # Comment pattern.
    'comment_pattern': r'^# ',

    # re.compiled object.
    'OPTION_PATTERN': None,

    # re.compiled object
    'SEPARATOR_PATTERN': None,

    # re.compiled object
    'COMMENT_PATTERN': None,
}


class Cell(Enum):
    MARKDOWN = 1
    CODE = 2
    SEPARATOR = 3

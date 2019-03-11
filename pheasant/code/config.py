from typing import Any, Dict
import re

config: Dict[str, Any] = {
    "code_pattern": r"#?!\[(.+?)\]\((.+?)\)",
    # Language-extensions
    "language": {"python": ["py"], "yaml": ["yml"]},
}

ESCAPE_PATTERN = re.compile(r"(```(.*?)```)|(~~~(.*?)~~~)", re.DOTALL)

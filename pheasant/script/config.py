from typing import Any, Dict

config: Dict[str, Any] = {
    # Option pattern.
    "option_pattern": r".*?(\s{2,}# -)(.+)$",
    # Comment pattern.
    "comment_pattern": r"^# ",
    # Separator expression.
    "separator_expr": "# -",
}

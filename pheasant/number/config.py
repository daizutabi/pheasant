from typing import Any, Dict

config: Dict[str, Any] = {
    # List of page absolute path in order.
    "pages": [],
    # Page path that matches this pattern will be ignored to number.
    "ignore_pattern": None,
    # List of ignored pages.
    "ignore_pages": [],
    # Jinja2 template file for numbering.
    "template_file": "basic.jinja2",
    # List of numbered objects
    "kind": ["header", "figure", "table", "code", "file"],
    # Whether header's number ends with a period or not
    "header_period": True,
    # Numbering level. 0 for multiple pages, 2 for h2 etc.
    "level": 2,
    # Prefix for numbered object.
    "kind_prefix": {},
    # Label file of reference to record reference infomation.
    "label_file": ".pheasant-number.json",
    # Begin pattern
    "begin_pattern": "<!-- begin -->",
    # End pattern
    "end_pattern": "<!-- end -->",
    # Label pattern.
    "class": "pheasant-number-{kind}",
    # <div> id name for numbered objects.
    "id": "pheasant-number-{label}",
    # relpath
    "relpath_function": None,
    # Markdown Extension to render header title.
    "markdown_extensions": [],
}

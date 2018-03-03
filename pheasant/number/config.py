from typing import Any, Dict

config: Dict[str, Any] = {
    # Jinja2 template file for numbering.
    'template_file': 'basic.jinja2',

    # List of numbered objects
    'kind': ['header', 'figure', 'table', 'code'],

    # Numbering level. 0 for multiple pages, 2 for h2 etc.
    'level': 2,

    # Prefix for numbered object.
    'kind_prefix': {},

    # Label file of reference to record reference infomation.
    'label_file': '.pheasant-number.json',

    # Begin patter
    'begin_pattern': '<!-- begin -->',

    # End patter
    'end_pattern': '<!-- end -->',

    # Label pattern.
    'label_pattern': r'\{#(\S+?)#\}',

    # <div> class name for numbered objects.
    'class': 'pheasant-number-{kind}',

    # <div> id name for numbered objects.
    'id': 'pheasant-number-{label}',

    # relpath
    'relpath_function': None,

    # Markdown Extension to render header title.
    'markdown_extensions': [],
}

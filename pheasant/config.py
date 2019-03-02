from typing import Any, Dict

from pheasant import code, jupyter, macro, number

# from .markdown import office

config: Dict[str, Any] = {
    # 'converters': [macro, jupyter, code, office, number],
    'converters': [macro, jupyter, code, number],

    # current source file
    'source_file': None,

    # current extra css list
    'extra_css': [],

    # current extra raw css list
    'extra_raw_css': [],

    # current extra javascript list
    'extra_javascript': [],

    # current extra raw javascript list
    'extra_raw_javascript': [],

    # source files set to remember which source file needs extra head.
    'extra_head': {
        'extra_css': set(),
        'extra_raw_css': set(),
        'extra_javascript': set(),
        'extra_raw_javascript': set()
    },
}

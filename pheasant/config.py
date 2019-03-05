from typing import Any, Dict

from pheasant import code, jupyter, macro, number

# from .markdown import office

config: Dict[str, Any] = {
    # 'converters': [macro, jupyter, code, office, number],
    'converters': [macro, jupyter, code, number],

    # current source file
    'source_file': None,

    # extra css list
    'extra_css': [],

    # extra raw css list
    'extra_raw_css': [],

    # extra javascript list
    'extra_javascript': [],

    # extra raw javascript list
    'extra_raw_javascript': [],
}

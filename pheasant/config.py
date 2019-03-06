from typing import Any, Dict

from pheasant import code, jupyter, macro, number

config: Dict[str, Any] = {
    # converters list in order of process.
    'converters': [macro, jupyter, code, number],

    # current source file
    'source_file': None,

    # extra resources for each page.
    # config['extra_resources'][abs_src_path]
    # keys: 'extra_css', 'extra_raw_css',
    #       'extra_javascript', 'extra_raw_javascript'
    'extra_resources': {},

    # MkDocs server
    'server': None
}

from typing import Any, Dict

from pheasant import code, jupyter, macro, number, script

config: Dict[str, Any] = {
    # Converters list in order of process.
    "converters": [script, macro, jupyter, code, number],
    # Absolute path of the current source file.
    "source_file": None,
    # Extra resources for each page.
    # config['extra_resources'][abs_src_path]
    # keys: 'extra_css', 'extra_raw_css',
    #       'extra_javascript', 'extra_raw_javascript'
    "extra_resources": {},
    # MkDocs server. Currently not used.
    "server": None,
}

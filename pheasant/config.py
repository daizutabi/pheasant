from typing import Any, Dict

from pheasant import code, jupyter, macro, number

# from .markdown import office

config: Dict[str, Any] = {
    # 'converters': [macro, jupyter, code, office, number],
    'converters': [macro, jupyter, code, number],
    'source_file': None,
}

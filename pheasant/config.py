from . import code, jupyter, macro, number
from .markdown import office

config = {
    'converters': [macro, jupyter, code, office, number],
    'source_file': None,
}

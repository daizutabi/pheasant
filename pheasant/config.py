from . import jupyter, macro, number, code
from .markdown import office

config = {
    'converters': [macro, jupyter, code, office, number],
    'source_file': None,
}

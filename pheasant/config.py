from . import jupyter, macro, number
from .markdown import office

config = {
    'converters': [macro, jupyter, office, number],
    'source_file': None,
}

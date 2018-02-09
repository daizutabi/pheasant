from . import debug, jupyter, macro, number, office

config = {
    'converters': [macro, jupyter, office, number, debug],
    'source_file': None,
}

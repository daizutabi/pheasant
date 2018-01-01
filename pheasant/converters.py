from .config import config as pheasant_config


def get_converters():
    return pheasant_config['converters']


def set_converters(converters):
    pheasant_config['converters'] = converters


def get_source_file():
    return pheasant_config['source_file']


def get_converter_name(converter):
    return converter.__name__.split('.')[-1]


def update_config(converter, config):
    if not hasattr(converter, 'config'):
        converter.config = {}

    if converter.config.get('configured', False):
        return

    converter.config['enabled'] = True
    converter_config = config.get(get_converter_name(converter),
                                  {'enabled': False})
    for key, value in converter_config.items():
        if isinstance(value, dict):
            converter.config[key].update(value)
        else:
            converter.config[key] = value
    if hasattr(converter, 'initialize'):
        converter.initialize()  # invoke converter's initializer
    converter.config['configured'] = True


def convert(source, config):
    pheasant_config['source_file'] = source
    for converter in pheasant_config['converters']:
        update_config(converter, config)
        if converter.config['enabled']:
            source = converter.convert(source) or source

    return source

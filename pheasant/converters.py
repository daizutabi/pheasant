import os
from typing import Dict, List, Optional

import yaml

from pheasant.config import config as pheasant_config
from pheasant.utils import read_source


def get_converters() -> list:
    return pheasant_config['converters']


def set_converters(converters: list) -> None:
    pheasant_config['converters'] = converters


def get_source_file() -> Optional[str]:
    return pheasant_config['source_file']


def get_converter_name(converter) -> str:
    return converter.__name__.split('.')[-1]


def update_config(converter, config: dict) -> None:
    if not hasattr(converter, 'config'):
        converter.config = {}

    if converter.config.get('configured', False):
        return

    name = get_converter_name(converter)
    if name in config:
        converter.config['enabled'] = True
        if isinstance(config[name], dict):
            for key, value in config[name].items():
                if isinstance(value, dict):
                    converter.config[key].update(value)
                else:
                    converter.config[key] = value
    else:
        converter.config['enabled'] = False

    if hasattr(converter, 'initialize'):
        converter.initialize()  # invoke converter's initializer

    converter.config['configured'] = True


def extra_keys() -> List[str]:
    return list(pheasant_config['extra_head'].keys())


def convert(source: str, config: Optional[dict] = None) -> str:
    # Reset extra resources
    for key in extra_keys():
        if source not in pheasant_config['extra_head'][key]:
            pheasant_config[key] = []

    pheasant_config['source_file'] = source
    source = read_source(source)  # Now source is always `str`.

    # Converter chain
    for converter in pheasant_config['converters']:
        update_config(converter, config or pheasant_config)
        if converter.config['enabled']:
            source = converter.convert(source) or source

    return source


def update_pheasant_config(path: str) -> None:
    """Update phesant config with a YAML file.

    Parameters
    ----------
    path
        YAML config file path.
    """
    if os.path.exists(path):
        with open(path) as f:
            pheasant_config.update(yaml.load(f))


def set_pheasant_config(config: Dict) -> None:
    """Set pheasant config to the plugin config object.

    Parameters
    ----------
    config
        The plugin config object.
    """
    keys = extra_keys()
    extra = {key: pheasant_config[key] for key in keys}
    config['pheasant'] = extra

    for key in keys:
        if pheasant_config[key]:
            pheasant_config['extra_head'][key].add(
                pheasant_config['source_file'])

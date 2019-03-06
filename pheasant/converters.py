import logging
import os
from typing import Optional

import yaml

from pheasant.config import config as pheasant_config
from pheasant.utils import read_source

logger = logging.getLogger('mkdocs')


def get_converters() -> list:
    return pheasant_config['converters']


def set_converters(converters: list) -> None:
    pheasant_config['converters'] = converters


def get_source_file() -> Optional[str]:
    return pheasant_config['source_file']


def get_converter_name(converter) -> str:
    return converter.__name__.split('.')[-1]


def update_pheasant_config(path: str = '',
                           config: Optional[dict] = None) -> None:
    """Update phesant config with a YAML file or config dict.

    Parameters
    ----------
    path
        YAML config file path.
    config
        The config dictionary.
    """
    if os.path.exists(path):
        with open(path) as f:
            pheasant_config.update(yaml.load(f))
    elif path:
        logger.warning("[Pheasant] Config file does not exist: '%s'", path)

    if config:
        pheasant_config.update(config)

    for key, value in pheasant_config.items():
        logger.debug("[Pheasant] Config value: '%s' = %r", key, value)


def update_page_config(config, source_file: str) -> None:
    """Update page config.

    Parameters
    ----------
    config
        The plugin config.
    source_file
        The abs source path for page.
    """
    if source_file in pheasant_config['extra_resources']:
        config['pheasant'] = pheasant_config['extra_resources'][source_file]
        logger.debug("[Pheasant] Extra resources added: %s", source_file)
    elif 'pheasant' in config:
        del config['pheasant']


def update_converter_config(converter, config: dict) -> None:
    if not hasattr(converter, 'config'):
        converter.config = {}

    if converter.config.get('configured', False):
        return

    name = get_converter_name(converter)

    if name in config:
        converter.config['enabled'] = True
        logger.debug("[Pheasant:%s] Enabled", name)
        if isinstance(config[name], dict):
            for key, value in config[name].items():
                if isinstance(value, dict):
                    converter.config[key].update(value)
                else:
                    converter.config[key] = value

        for key, value in converter.config.items():
            logger.debug("[Pheasant:%s] Config value: '%s' = %r",
                         name, key, value)
    else:
        converter.config['enabled'] = False
        logger.debug("[Pheasant:%s] Disabled", name)

    if hasattr(converter, 'initialize'):
        converter.initialize()  # invoke converter's initializer
        logger.debug("[Pheasant:%s] Initialized", name)

    converter.config['configured'] = True
    logger.debug("[Pheasant:%s] Configured", name)


def convert(source: str, config: Optional[dict] = None) -> str:
    logger.debug("[Pheasant] Start conversion: %s", source)
    pheasant_config['source_file'] = source
    source = read_source(source)  # Now source is always `str`.

    # Converter chain
    for converter in pheasant_config['converters']:
        update_converter_config(converter, config or pheasant_config)
        if converter.config['enabled']:
            name = get_converter_name(converter)
            logger.debug("[Pheasant:%s] Start conversion", name)
            source = converter.convert(source) or source
            logger.debug("[Pheasant:%s] End conversion", name)

    logger.debug("[Pheasant] End conversion: %s",
                 pheasant_config['source_file'])

    return source

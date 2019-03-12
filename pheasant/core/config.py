import importlib
import logging
from typing import Any, Dict, Optional


logger = logging.getLogger("mkdocs")

config: Dict[str, Any] = {
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


def get_source_file() -> Optional[str]:
    return config["source_file"]


def update_client_config(config: dict) -> None:
    """Update client config with a config dict.

    This function is called from a Plugin to configure Pheasant.

    The `pheasant_config` is the master config dictionary and the settings
    will be distributed to each converter later when it enables.

    Parameters
    ----------
    path
        YAML config file path.
    config
        The config dictionary.
    """
    for client, client_config in config.items():
        logger.info("[Pheasant.%s] Enabled", client)
        module = importlib.import_module(f"pheasant.{client}.client")
        Client = getattr(module, client[0].upper() + client[1:])
        client = Client(client_config)
        for key, value in client.config.items():
            logger.debug(
                "[Pheasant.%s] Config value: '%s' = %r", client.name, key, value
            )


def update_page_config(config, source_file: str) -> None:
    """Update page config.

    This function is called in order to set extra resources such as
    css, javascript. Eash page has its own extra resources which the
    page actually requires.

    Parameters
    ----------
    config
        The plugin config.
    source_file
        The abs source path for page.
    """
    from pheasant.core.config import config as pheasant_config

    if source_file in pheasant_config["extra_resources"]:
        config["pheasant"] = pheasant_config["extra_resources"][source_file]
        logger.debug("[Pheasant] Extra resources added: %s", source_file)
    elif "pheasant" in config:
        del config["pheasant"]


# def update_client_config(client: Client, config: dict) -> None:
#     """Update each converter's specific config.
#
#     Configuration is made once for each converter. After configuration,
#     the `initialize` function is invoked if the converter has it.
#     """
#     if client.config.get("configured", False):
#         return
#
#     name = client.name
#
#     if name in config:
#         client.config["enabled"] = True
#         logger.debug("[Pheasant:%s] Enabled", name)
#         if isinstance(config[name], dict):
#             for key, value in config[name].items():
#                 if isinstance(value, dict):
#                     converter.config[key].update(value)
#                 else:
#                     converter.config[key] = value
#
#         for key, value in converter.config.items():
#             logger.debug("[Pheasant:%s] Config value: '%s' = %r", name, key, value)
#     else:
#         converter.config["enabled"] = False
#         logger.debug("[Pheasant:%s] Disabled", name)
#
#     if hasattr(converter, "initialize"):
#         converter.initialize()  # invoke converter's initializer
#         logger.debug("[Pheasant:%s] Initialized", name)
#
#     converter.config["configured"] = True
#     logger.debug("[Pheasant:%s] Configured", name)

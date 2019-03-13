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

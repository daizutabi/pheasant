import logging
import os
from typing import Dict

import yaml
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

from pheasant.core.converter import Converter

config_options  # to avoid linter error.

logger = logging.getLogger("mkdocs")


class PheasantPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config: Dict[str, Dict[str, str]] = {}
        self.converter = Converter()
        self.served = False
        logger.debug("[Pheasant] Plugin created.")

    def on_serve(self, server, config):
        self.served = True

        return server

    def on_config(self, config):
        from mkdocs.utils import markdown_extensions

        markdown_extensions.append(".py")

        logger.debug("[Pheasant] Plugin enabled.")
        path = os.path.dirname(config["config_file_path"])
        path = os.path.join(path, "pheasant.yml")
        if os.path.exists(path):
            logger.debug(f"[Pheasant] config file: {path}")
            with open(path, "r") as f:
                self.config = yaml.load(f)
            for key, value in self.config.items():
                for key_, value_ in value.items():
                    logger.debug(f"[Pheasant.{key}] Config value: '{key_}' = {value_}.")

        return config

    def on_nav(self, nav, config, files):
        self.config["abs_src_paths"] = [page.file.abs_src_path for page in nav.pages]
        self.config["src_paths"] = [page.file.src_path for page in nav.pages]
        for k, srs_path in enumerate(self.config["src_paths"]):
            logger.debug(f"[Pheasant] Page #{k + 1}: {srs_path}")

        return nav

    def on_page_read_source(self, source, page, config):
        """
        The on_page_read_source event can replace the default mechanism
        to read the contents of a page's source from the filesystem.

        Parameters
        ----------
        source: None
        page: mkdocs.nav.Page instance
        config: global configuration object

        Returns
        -------
        The raw source for a page as unicode string. If None is returned, the
        default loading from a file will be performed.
        """
        logger.info(f"[Pheasant] Converting: {page.file.src_path}")
        source = self.converter.convert(page.file.abs_src_path)

        return source

    def on_page_context(self, context, page, config, nav):
        logger.info(f"Uso [Pheasant] Updating config: {page.file.src_path}")
        # update_page_config(config, page.file.abs_src_path)
        return context

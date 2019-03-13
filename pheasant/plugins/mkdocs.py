import logging
import os

import yaml
from mkdocs.config import config_options  # This import required for BasePlugin
from mkdocs.plugins import BasePlugin

from pheasant.core.config import update_page_config
from pheasant.core.converter import convert, converter, start_client

# from pheasant.number.converter import register_pages

config_options  # to avoid linter error.

logger = logging.getLogger("mkdocs")


class PheasantPlugin(BasePlugin):
    # def on_serve(self, server, config):
    #     update_pheasant_config(config={"server": server})
    #
    #     return server

    def on_config(self, config):
        from mkdocs.utils import markdown_extensions

        markdown_extensions.append(".py")

        logger.debug("[Pheasant] Pheasant plugin enabled.")
        path = os.path.dirname(config["config_file_path"])
        path = os.path.join(path, "pheasant.yml")
        if os.path.exists(path):
            logger.debug(f"[Pheasant] Pheasant config file: {path}")
            with open(path) as f:
                client_config = yaml.load(f)
        elif path:
            logger.warning("[Pheasant] Config file does not exist: '%s'", path)
            client_config = {"jupyter": None}

        for name, config_ in client_config.items():
            start_client(name, config_)

        return config

    def on_nav(self, nav, config, files):
        if "number" in converter.clients:
            client = converter.clients["number"]
            abs_src_paths = [page.file.abs_src_path for page in nav.pages]
            client.register_pages(abs_src_paths)

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
        if "number" in converter.clients:
            client = converter.clients["number"]
            client.on_page_read_source(page.file.abs_src_path)
        source = convert(page.file.abs_src_path)

        return source

    def on_page_context(self, context, page, config, nav):
        update_page_config(config, page.file.abs_src_path)
        return context

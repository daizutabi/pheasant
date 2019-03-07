import logging
import os

from mkdocs.config import config_options  # This import required for BasePlugin
from mkdocs.plugins import BasePlugin

from pheasant.converters import (convert, update_page_config,
                                 update_pheasant_config)
from pheasant.number.converter import register_pages

config_options  # to avoid linter error.

logger = logging.getLogger('mkdocs')


class PheasantPlugin(BasePlugin):
    def on_serve(self, server, config):
        update_pheasant_config(config={'server': server})

        return server

    def on_config(self, config):
        from mkdocs.utils import markdown_extensions
        markdown_extensions.append('.py')

        logger.debug('[Pheasant] Pheasant plugin enabled.')
        path = os.path.dirname(config['config_file_path'])
        path = os.path.join(path, 'pheasant.yml')
        logger.debug(f'[Pheasant] Pheasant config file: {path}')
        update_pheasant_config(path=path)

        return config

    def on_nav(self, nav, config, files):
        source_files = [page.file.abs_src_path for page in nav.pages]
        register_pages(source_files)

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
        logger.info(f'[Pheasant] Converting: {page.file.src_path}')
        source = convert(page.file.abs_src_path)

        return source

    def on_page_context(self, context, page, config, nav):
        update_page_config(config, page.file.abs_src_path)
        return context

import logging
import os

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

from pheasant.converters import (convert, set_pheasant_config,
                                 update_pheasant_config)

logger = logging.getLogger('pheasant')
config_options  # for BasePlugin


class PheasantPlugin(BasePlugin):
    def on_config(self, config):
        if 'pheasant' in config['plugins']:
            path = os.path.dirname(config['config_file_path'])
            path = os.path.join(path, 'pheasant.yml')
            update_pheasant_config(path)

            # Add pheasant theme for dynamic css and javascript link
            theme = config['theme']
            path = os.path.abspath(os.path.join(__file__, '../../theme'))
            theme.dirs = [path] + theme.dirs
            config['thema'] = theme

        return config

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
        logger.info(f'Converting: {page.file.src_path}')

        source = convert(page.file.abs_src_path)
        set_pheasant_config(config)

        return source

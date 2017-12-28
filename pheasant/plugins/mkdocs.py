import logging

from mkdocs.plugins import BasePlugin
from pheasant import convert, set_config

logger = logging.getLogger('mkdocs')


class PheasantPlugin(BasePlugin):

    def on_config(self, config):
        """
        The config event is the first event called on build and is run
        immediately after the user configuration is loaded and validated.
        Any alterations to the config should be made here.

        Parameters
        ----------
        config: global configuration object

        Returns
        -------
        global configuration object
        """
        set_config(config['plugins']['pheasant'].config)
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
        logger.info(f'[pheasant] Converting: {page.abs_input_path}')
        return convert(page.abs_input_path)

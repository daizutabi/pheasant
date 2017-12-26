import logging
from html import escape

import nbformat

from pheasant.config import config as pheasant_config
from pheasant.core.markdown import convert as convert_markdown
from pheasant.core.notebook import convert as convert_notebook
from pheasant.mkdocs.defaults import DEFAULT_SCHEMA

try:
    from mkdocs.plugins import BasePlugin
except ImportError:
    BasePlugin = object


logger = logging.getLogger('mkdocs')


class PheasantPlugin(BasePlugin):
    config_scheme = DEFAULT_SCHEMA

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pheasant_markdown = None

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
        plugin_config = config['plugins']['pheasant'].config
        if plugin_config['template_file']:
            template = plugin_config['template_file']
            pheasant_config['jupyter']['template'] = template
            logger.info(f'Template file for pheasant: {template}')

        pheasant_config['jupyter']['kernel_name'].update(
            plugin_config['kernel_name'])

        return config

    def on_serve(self, server, config):
        """
        The serve event is only called when the serve command is used during
        development. It is passed the Server instance which can be modified
        before it is activated. For example, additional files or directories
        could be added to the list of "watched" filed for auto-reloading.

        Parameters
        ----------
        server: livereload.Server instance
        config: global configuration object

        Return
        -------
        livereload.Server instance
        """
        return server

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
        notebook = page.abs_input_path
        if not notebook.endswith('.ipynb'):
            return
        logger.info(f'[pheasant] Converting notebook: {notebook}')
        markdown = convert_notebook(notebook)
        self._pheasant_markdown = markdown
        return markdown

    def on_page_markdown(self, markdown, page, config, site_navigation):
        """
        The page_markdown event is called after the page's markdown is loaded
        from file and can be used to alter the Markdown source text.
        The meta-data has been stripped off and is available as page.meta
        at this point.

        Parameters
        ----------

        markdown: Markdown source text of page as string
        page: mkdocs.nav.Page instance
        config: global configuration object
        site_navigation: global navigation object

        Returns
        -------
        Markdown source text of page as string
        """
        path = page.abs_input_path
        if path.endswith('.ipynb'):
            return markdown

        msg = f'[pheasant] Converting markdown: {path}'
        logger.info(msg)
        markdown = convert_markdown(markdown)
        self._pheasant_markdown = markdown
        return markdown

    def on_page_content(self, html, page, config, site_navigation):
        """
        The page_content event is called after the Markdown text is rendered
        to HTML (but before being passed to a template) and can be used to
        alter the HTML body of the page.

        Parameters
        ----------
        html: HTML rendered from Markdown source as string
        page: mkdocs.nav.Page instance
        config: global configuration object
        site_navigation: global navigation object

        Returns
        -------
        HTML rendered from Markdown source as string
        """
        plugin_config = config['plugins']['pheasant'].config
        if plugin_config.get('debug', False) and self._pheasant_markdown:
            html = escape(self._pheasant_markdown)
            html = f'<h1>DEBUG MODE</h1><pre>{html}</pre>'

        return html

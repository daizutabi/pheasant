import logging
from html import escape

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from pheasant import config as pheasant_config
from pheasant import convert

logger = logging.getLogger('mkdocs')


DEFAULT_SCHEMA = (
    ('output_format', config_options.Type(
        utils.string_types, default='html')),
    ('template_file', config_options.Type(
        utils.string_types, default='')),
    ('kernel_name', config_options.Type(
        dict, default={'python', 'python3'})),
)


class PheasantPlugin(BasePlugin):
    config_scheme = DEFAULT_SCHEMA

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pheasant_source = None
        self._pheasant_output = None

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

        self._pheasant_output = plugin_config['output_format']

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
        notebook = page.abs_input_path
        if not notebook.endswith('.ipynb'):
            return

        logger.info(f'[pheasant] Converting notebook: {notebook}')
        # source = convert_notebook(notebook, output=self._pheasant_output)
        source = convert(notebook, output=self._pheasant_output)
        if not isinstance(source, str):
            source = str(source)
        self._pheasant_source = source
        return source

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
        source = convert(markdown, output=self._pheasant_output)
        if not isinstance(source, str):
            source = str(source)
        self._pheasant_source = source
        return source

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
        if self._pheasant_output != 'html' and self._pheasant_source:
            html = escape(self._pheasant_source)
            html = f'<h1>DEBUG MODE</h1><pre>{html}</pre>'

        return html

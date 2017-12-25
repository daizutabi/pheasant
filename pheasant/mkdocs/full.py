import logging

try:
    from mkdocs.plugins import BasePlugin
except ImportError:
    BasePlugin = object

logger = logging.getLogger('mkdocs')


def message(key, value):
    logger.info(f'[pheasant] {key}: {value}')


class JupyterPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = None
        self.site_navigation = None

    def update_config(self, event, config):
        if self.config != config:
            self.config = config.copy()
            message(f'on_{event}.config', self.config)

    def update_site_navigation(self, event, site_navigation):
        if self.site_navigation != site_navigation:
            self.site_navigation = site_navigation
            message(f'on_{event}.site_navigation', self.site_navigation)

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
        self.update_config('config', config)
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
        message('serve.server', server)
        self.update_config('serve', config)
        return server

    def on_pre_build(self, config):
        """
        The pre_build event does not alter any variables. Use this event to
        call pre-build scripts.

        Parameters
        ----------
        config: global configuration object
        """
        self.update_config('pre_build', config)

    def on_nav(self, site_navigation, config):
        """
        The nav event is called after the site navigation is created and can
        be used to alter the site navigation.

        Parameters
        ----------
        site_navigation: global navigation object
        config: global configuration object

        Returns
        -------
        site_navigation: global navigation object
        """
        self.update_site_navigation('nav', site_navigation)
        self.update_config('nav', config)
        return site_navigation

    def on_env(self, env, config, site_navigation):
        """
        The env event is called after the Jinja template environment is
        created and can be used to alter the Jinja environment.

        Parameters
        ----------
        env: global Jinja environment
        config: global configuration object
        site_navigation: global navigation object

        Returns
        -------
        global Jinja Environment
        """
        message('env.env', env)
        self.update_site_navigation('env', site_navigation)
        self.update_config('env', config)
        return env

    def on_post_build(self, config):
        """
        The post_build event does not alter any variables. Use this event to
        call post-build scripts.

        Parameters
        ----------
        config: global configuration object
        """
        self.update_config('post_build', config)

    def on_pre_template(self, template, template_name, config):
        """
        The pre_template event is called immediately after the subject template
        is loaded and can be used to alter the content of the template.

        Parameters
        ----------
        template: the template contents as string
        template_name: string filename of template
        config: global configuration object

        Returns
        -------
        template contents as string
        """
        event = 'pre_template'
        message(f'{event}:template', template)
        message(f'{event}:template_name', template_name)
        self.update_config(event, config)
        return template

    def on_template_context(self, context, template_name, config):
        """
        The template_context event is called immediately after the context is
        created for the subject template and can be used to alter the context
        for that specific template only.

        Parameters
        ----------
        context: dict of template context variables
        template_name: string filename of template
        config: global configuration object

        Returns
        -------
        dict of template context variables
        """
        event = 'template_context'
        message(f'{event}:context', context)
        message(f'{event}:template_name', template_name)
        self.update_config(event, config)
        return context

    def on_post_template(self, output_content, template_name, config):
        """
        The post_template event is called after the template is rendered, but
        before it is written to disc and can be used to alter the output of the
        template. If an empty string is returned, the template is skipped and
        nothing is is written to disc.

        Parameters
        ----------
        output_content: output of rendered template as string
        template_name: string filename of template
        config: global configuration object

        Returns
        -------
        output of rendered template as string
        """
        event = 'post_template'
        message(f'{event}:output_content', output_content)
        message(f'{event}:template_name', template_name)
        self.update_config(event, config)
        return output_content

    def on_pre_page(self, page, config, site_navigation):
        """
        The pre_page event is called before any actions are taken on the
        subject page and can be used to alter the Page instance.

        Parameters
        ----------
        page: mkdocs.nav.Page instance
        config: global configuration object
        site_navigation: global navigation object

        Returns
        -------
        mkdocs.nav.Page instance
        """
        event = 'pre_page'
        message(f'{event}:page', page)
        self.update_config(event, config)
        self.update_site_navigation(event, site_navigation)
        return page

    # def on_page_read_source(self, page, config):
    #     """
    #     The on_page_read_source event can replace the default mechanism
    #     to read the contents of a page's source from the filesystem.
    #
    #     Parameters
    #     ----------
    #     page: mkdocs.nav.Page instance
    #     config: global configuration object
    #
    #     Returns
    #     -------
    #     The raw source for a page as unicode string. If None is returned, the
    #     default loading from a file will be performed.
    #     """
    #     event = 'page_read_source'
    #     message(f'{event}:page', page)
    #     self.update_config(event, config)
    #     return None

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
        event = 'page_markdown'
        message(f'{event}:markdown', markdown)
        message(f'{event}:page', page)
        self.update_config(event, config)
        self.update_site_navigation(event, site_navigation)
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
        event = 'page_content'
        message(f'{event}:html', html)
        message(f'{event}:page', page)
        self.update_config(event, config)
        self.update_site_navigation(event, site_navigation)
        return html

    def on_page_context(self, context, page, config, site_navigation):
        """
        The page_context event is called after the context for a page is
        created and can be used to alter the context for that specific page
        only.

        Parameters
        ----------
        context: dict of template context variables
        page: mkdocs.nav.Page instance
        config: global configuration object
        site_navigation: global navigation object

        Returns
        -------
        dict of template context variables
        """
        event = 'page_context'
        message(f'{event}:context', context)
        message(f'{event}:page', page)
        self.update_config(event, config)
        self.update_site_navigation(event, site_navigation)
        return context

    def on_post_page(self, output_content, page, config):
        """
        No documentation

        Parameters
        ----------
        output_content: output of rendered template as string
        page: mkdocs.nav.Page instance
        config: global configuration object

        Returns
        -------
        output of rendered template as string
        """
        event = 'post_page'
        message(f'{event}:output_content', output_content)
        message(f'{event}:page', page)
        self.update_config(event, config)
        return output_content

import logging
import os

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import get_files
from mkdocs.utils import string_types

import pheasant
from pheasant.core.pheasant import Pheasant
from pheasant.jupyter.client import execution_report

logger = logging.getLogger("mkdocs")


class PheasantPlugin(BasePlugin):
    config_scheme = (
        ("foo", config_options.Type(string_types, default="a default value")),
        ("bar", config_options.Type(int, default=0)),
        ("baz", config_options.Type(bool, default=True)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("[Pheasant] Plugin created.")
        self.converter = Pheasant()
        logger.debug(f"[Pheasant] Converter created. {self.converter}")
        for name, parser in self.converter.parsers.items():
            logger.debug(f"[Pheasant] Parser for '{name}' = {parser}.")
        logger.debug("[Pheasant] Renderer registered.")
        for name, renderers in self.converter.renderers.items():
            logger.debug(f"[Pheasant] Renderers for '{name}' = {renderers}.")

        from mkdocs.utils import markdown_extensions

        markdown_extensions.append(".py")
        logger.debug(
            f"[Pheasant] `mkdocs.utils.markdown_extensions` = {markdown_extensions}"
        )

    def on_serve(self, server, **kwargs):
        watcher = server.watcher
        builder = list(watcher._tasks.values())[0]["func"]
        root = os.path.join(os.path.dirname(pheasant.__file__), "themes/mkdocs")
        server.watch(root, builder)

        return server

    def on_config(self, config, **kwargs):
        if self.config:
            self.converter.update_config(self.config)

        if "extra_css" not in self.config:
            self.config["extra_css"] = config["extra_css"]
            self.config["extra_javascript"] = config["extra_javascript"]

        return config

    def on_files(self, files, config):
        root = os.path.join(os.path.dirname(pheasant.__file__), "themes/mkdocs")
        docs_dir = config["docs_dir"]
        config["docs_dir"] = root
        files_ = get_files(config)
        config["docs_dir"] = docs_dir

        config["extra_css"] = list(self.config["extra_css"])
        config["extra_javascript"] = list(self.config["extra_javascript"])

        for file in files_:
            files.append(file)
            path = file.src_path.replace("\\", "/")
            if path.endswith(".css"):
                config["extra_css"].insert(0, path)
            else:
                config["extra_javascript"].insert(0, path)

        config["extra_css"].append(
            "https://cdn.jsdelivr.net/gh/tonsky/FiraCode@1.206/distr/fira_code.css"
        )
        logger.info(f"[Pheasant] extra_css altered: {config['extra_css']}")

        return files

    def on_nav(self, nav, config, **kwargs):
        def message(msg):
            logger.debug(f"[Pheasant] {msg}")

        paths = [page.file.abs_src_path for page in nav.pages]
        logger.info(f"[Pheasant] Converting: Page number = {len(paths)}.")
        self.converter.convert_from_files(paths, message=message)
        logger.info(f"[Pheasant] Kernel execution time: {execution_report['total']}")

        return nav

    def on_page_read_source(self, source, page, **kwargs):
        return self.converter.pages[page.file.abs_src_path].output

    def on_page_content(self, content, page, **kwargs):
        return "\n".join(
            [self.converter.pages[page.file.abs_src_path].meta["extra_html"], content]
        )

    def on_post_page(self, output, **kwargs):
        return output.replace('.js" defer></script>', '.js"></script>')


def _emulate_mkdocs_main_and_build():
    from mkdocs.config import load_config
    from mkdocs.structure.files import get_files
    from mkdocs.structure.nav import get_navigation
    from mkdocs.commands.build import get_context

    # in main function
    config_file = "C:/Users/daizu/Desktop/test/mkdocs.yml"
    config = load_config(config_file)
    config["site_dir"]

    # in build function
    # Run `config` plugin events.
    # Run `pre_build` plugin events.
    files = get_files(config)
    env = config["theme"].get_env()
    files.add_files_from_theme(env, config)
    files
    # Run `files` plugin events.
    nav = get_navigation(files, config)
    # Run `nav` plugin events.
    nav = config["plugins"].run_event("nav", nav, config=config, files=files)
    #  -> Here! Pheasant preprocesses source for all `nav.pages`

    # _populate_page(file.page, config, files, dirty)
    for file in files.documentation_pages():
        page = file.page
        # Run the `pre_page` plugin event
        # Run `page_read_source` plugin events.
        #   -> Here! Pheasant returns the preprocessed source
        page.read_source(config)
        # Run `page_markdown` plugin events.
        page.render(config, files)
        # Run `page_content` plugin events.

    # pheasant = config["plugins"]["pheasant"]
    # pheasant.converter.jupyter.meta

    # Run `env` plugin events.
    #  -> Here! Pheasant postrocesses page and template for all pages
    #    'main.html' or page.meta['template']
    #     extra resources for each page.

    # _build_page(file.page, config, files, nav, env, dirty)
    for file in files.documentation_pages():
        page = file.page
        page.active = True
        context = get_context(nav, files, config, page)

        # Allow 'template:' override in md source files.
        if "template" in page.meta:
            template = env.get_template(page.meta["template"])
        else:
            template = env.get_template("main.html")

        # Run `page_context` plugin events.

        # Render the template.
        output = template.render(context)

        # NOT MKDOCS SOURCE BELOW
        page.output = output

        # Run `post_page` plugin events.
        # Deactivate page
        page.active = False

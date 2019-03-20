import logging
import os

import yaml
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import string_types

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
        # for name, parser in self.converter.parsers.items():
        #     logger.debug(f"[Pheasant] Parser for '{name}' = {parser}.")
        # logger.debug("[Pheasant] Renderer registered.")
        # for name, renderers in self.converter.renderers.items():
        #     logger.debug(f"[Pheasant] Renderers for '{name}' = {renderers}.")
        from mkdocs.utils import markdown_extensions

        markdown_extensions.append(".py")
        logger.debug("[Pheasant] Python source files will be captured.")

    def on_serve(self, server, config):
        return server

    def on_config(self, config):
        logger.info(f"[Pheasant] on_config")
        logger.debug("[Pheasant] Plugin enabled.")

        path = os.path.dirname(config["config_file_path"])
        path = os.path.join(path, "pheasant.yml")
        if os.path.exists(path):
            logger.debug(f"[Pheasant] Config file: {path}")
            # with open(path, "r") as f:
            #     config_ = yaml.load(f)
            # for renderer in self.converter.renderers:
            #     name = renderer.name
            #     if name in config_:
            #         renderer.update_config(config_[name])
            #     for key, value in renderer.config.items():
            #         logger.debug(f"[Pheasant.{name}] Config value: '{key}' = {value}.")
            #     renderer.init()
            #     logger.debug(f"[Pheasant.{name}] Initialized.")

        env = config["theme"].get_env()
        print(env)
        template = env.get_template('main.html')
        print(template)
        return config

    def on_pre_build(self, config):
        logger.info(f"[Pheasant] on_pre_build")
        # print(self.config)
        # implement "bool_option" functionality here...

    def on_nav(self, nav, config, files):
        logger.debug(f"[Pheasant] Page order for numbering.")
        for page in nav.pages:
            logger.info(f"[Pheasant] Page order: {page.file.src_path}")

        # self.config["abs_src_paths"] = [page.file.abs_src_path for page in nav.pages]
        # self.config["src_paths"] = [page.file.src_path for page in nav.pages]
        # for k, srs_path in enumerate(self.config["src_paths"]):
        #     logger.debug(f"[Pheasant] Page number {k + 1}: {srs_path}")

        return nav

    def on_page_read_source(self, source, page, config):
        logger.info(f"[Pheasant] on_page_read_source: {page.file.src_path}")
        return source

    def on_page_markdown(self, markdown, page, config, files):
        logger.info(f"[Pheasant] on_page_markdown: {page.file.src_path}")
        print(markdown)
        return markdown

    def on_page_content(self, content, page, config, files):
        logger.info(f"[Pheasant] on_page_content: {page.file.src_path}")
        print(content)
        return content

    def on_page_context(self, context, page, config, nav):
        logger.info(f"[Pheasant] on_page_context: {page.file.src_path}")
        print(context.keys())
        print(context["config"] == config)
        # update_page_config(config, page.file.abs_src_path)
        return context

    def on_post_page(self, output, page, config):
        logger.info(f"[Pheasant] on_post_page: {page.file.src_path}")
        # print(output)
        return output

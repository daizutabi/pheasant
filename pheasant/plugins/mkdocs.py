import logging
import os

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
from mkdocs.utils import string_types

import pheasant
from pheasant.core.pheasant import Pheasant

logger = logging.getLogger("mkdocs")


class PheasantPlugin(BasePlugin):
    config_scheme = (
        ("foo", config_options.Type(string_types, default="a default value")),
        ("bar", config_options.Type(int, default=0)),
        ("baz", config_options.Type(bool, default=True)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("[Pheasant] Plugin created.")
        self.converter = Pheasant()
        logger.info(f"[Pheasant] Converter created. {self.converter}")
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

    # def on_serve(self, server, **kwargs):
    #     logger.debug(f"[Pheasant] on_pre_build")
    #     return server

    def on_config(self, config, **kwargs):
        logger.info(f"[Pheasant] on_config: config={self.config}")
        if self.config:
            self.converter.update_config(self.config)

        # Remember original extra_css, extra_javascript
        self.config["extra_css"] = list(config["extra_css"])
        self.config["extra_javascript"] = list(config["extra_javascript"])

        return config

    def on_nav(self, nav, config, **kwargs):

        def message(msg):
            logger.info(f"[Pheasant] {msg}")

        logger.info(f"[Pheasant] on_nav")
        logger.info(f"[Pheasant] Preprocess begins.")
        paths = [page.file.abs_src_path for page in nav.pages]
        self.converter.convert_from_files(paths, message=message)
        logger.info(f"[Pheasant] Preprocess done.")

        for directory in ["css", "js"]:
            root = os.path.join(config["site_dir"], directory)
            if not os.path.exists(root):
                os.mkdir(root)

        docs_dir = os.path.join(os.path.dirname(pheasant.__file__), "themes/mkdocs")
        extra = {"css": [], "js": []}
        for key in extra:
            for path in os.listdir(os.path.join(docs_dir, key)):
                path_ = "/".join([key, path])
                file = File(
                    path_, docs_dir, config["site_dir"], config["use_directory_urls"]
                )
                file.copy_file()
                extra[key].append(path_)

        for page in nav.pages:
            page_ = self.converter.pages[page.file.abs_src_path]
            extra_resources = page_.meta["extra_resources"]

            for key in ["extra_raw_css", "extra_raw_javascript"]:
                if extra_resources[key]:
                    ext = "css" if "css" in key else "js"
                    path = "-".join(extra_resources["modules"])
                    path = f"{ext}/{path}.{ext}"
                    abs_path = os.path.join(config["site_dir"], path)
                    if not os.path.exists(abs_path):
                        source = "\n".join(extra_resources[key])
                        with open(abs_path, "w", encoding="utf8") as file:
                            file.write(source)
                    extra_resources[key.replace("_raw", "")].append(path)
                    if ext == "css":
                        # Reload
                        theme_css = ["css/theme.css", "css/theme_extra.css"]
                        extra_resources["extra_css"].extend(theme_css)
                del extra_resources[key]

            extra_resources["extra_css"].extend(extra["css"])
            extra_resources["extra_javascript"].extend(extra["js"])

    def on_page_read_source(self, source, page, **kwargs):
        assert source is None
        logger.info(
            f"[Pheasant] on_page_read_source: {page.file.src_path}  -- "
            f"[Pheasant] Return preprocessed markdown"
        )

        return self.converter.pages[page.file.abs_src_path].output

    # def on_page_markdown(self, markdown, page, **kwargs):
    #     logger.info(f"[Pheasant] on_page_markdown: {page.file.src_path}")
    #     return markdown
    #
    # def on_page_content(self, content, page, **kwargs):
    #     logger.info(f"[Pheasant] on_page_content: {page.file.src_path}")
    #     return content

    def on_page_context(self, context, page, **kwargs):
        logger.info(f"[Pheasant] on_page_context: {page.file.src_path}")
        page_ = self.converter.pages[page.file.abs_src_path]
        for key in ["extra_css", "extra_javascript"]:
            context["config"][key] = list(self.config[key])
            context["config"][key].extend(page_.meta["extra_resources"][key])
        return context

    # Run `env` plugin events.
    def on_env(self, env, files, **kwargs):
        logger.info(f"[Pheasant] on_env")


def _emulate_mkdocs_main_and_build():
    from mkdocs.config import load_config
    from mkdocs.structure.files import get_files
    from mkdocs.structure.nav import get_navigation
    from mkdocs.commands.build import get_context

    # in main function
    config_file = "C:/Users/daizu/Desktop/test/mkdocs.yml"
    config = load_config(config_file)

    # in build function
    # Run `config` plugin events.
    # Run `pre_build` plugin events.
    files = get_files(config)
    env = config["theme"].get_env()
    files.add_files_from_theme(env, config)
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

    # theme = Theme("readthedocs")
    # theme.name
    # theme.dirs  # change
    # env = theme.get_env()  # make env
    # env.list_templates(extensions=["html"])
    # template_main = env.get_template("main.html")
    # path = template_main.filename
    # with codecs.open(path, "r", encoding="utf8") as file:
    #     source = file.read()
    #
    # pattern = (
    #     f"{env.block_start_string} +extends +[\"'](.*?)[\"'] +{env.block_end_string}"
    # )
    # pattern
    # base_path = re.search(pattern, source).group(1)
    # assert base_path == "base.html"
    #
    # template_base = env.get_template(base_path)
    # loader = env.loader
    # loader.get_source(env, base_path)

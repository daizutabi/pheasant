import logging
import os

import yaml
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import get_files
from mkdocs.utils import markdown_extensions, string_types

import pheasant
from pheasant.core.pheasant import Pheasant

logger = logging.getLogger("mkdocs")

markdown_extensions.append(".py")


class PheasantPlugin(BasePlugin):
    config_scheme = (
        ("foo", config_options.Type(string_types, default="a default value")),
        ("bar", config_options.Type(int, default=0)),
        ("baz", config_options.Type(bool, default=True)),
    )
    converter = Pheasant()
    logger.info(f"[Pheasant] Converter created.")

    def on_config(self, config, **kwargs):
        if self.config:
            self.converter.update_config(self.config)

        self.config["extra_css"] = config["extra_css"]
        self.config["extra_javascript"] = config["extra_javascript"]

        logger.info(f"[Pheasant] Converter configured.")
        return config

    def on_files(self, files, config):
        root = os.path.join(os.path.dirname(pheasant.__file__), "theme")
        docs_dir = config["docs_dir"]
        config["docs_dir"] = root
        files_ = get_files(config)
        config["docs_dir"] = docs_dir

        css = []
        js = []
        for file in files_:
            path = file.src_path.replace("\\", "/")
            if path.endswith(".css"):
                files.append(file)
                css.append(path)
            elif path.endswith(".js"):
                files.append(file)
                js.append(path)
            elif path.endswith(".yml"):
                path = os.path.normpath(os.path.join(root, path))
                with open(path) as f:
                    data = yaml.safe_load(f)
                css = data.get("extra_css", []) + css
                js = data.get("extra_javascript", []) + js

        config["extra_css"] = css + list(self.config["extra_css"])
        config["extra_javascript"] = js + list(self.config["extra_javascript"])

        return files

    def on_nav(self, nav, config, **kwargs):
        def message(msg):
            logger.info(f"[Pheasant] {msg}".replace(config["docs_dir"], ""))

        skipped = any(page.title.endswith("*") for page in nav.pages)
        if skipped:
            paths = []
            for page in nav.pages:
                if not page.title.endswith("*"):
                    message(f"Skip conversion: {page.file.abs_src_path}.")
                else:
                    page.title = page.title[:-1]
                    paths.append(page.file.abs_src_path)
        else:
            paths = [page.file.abs_src_path for page in nav.pages]

        logger.info(f"[Pheasant] Converting {len(paths)} pages.")
        self.converter.convert_from_files(paths, message=message)
        func_time = self.converter.convert_from_files.func_time
        kernel_time = self.converter.convert_from_files.kernel_time
        time = f"total: {func_time}, kernel: {kernel_time}"
        msg = "Conversion finished:" + " " * 26 + f"{time} "
        message(msg)

        return nav

    def on_page_read_source(self, source, page, **kwargs):
        try:
            return self.converter.pages[page.file.abs_src_path].output
        except KeyError:
            return "XXX"

    def on_page_content(self, content, page, **kwargs):
        if page.file.abs_src_path not in self.converter.pages:
            return content

        return "\n".join(
            [self.converter.pages[page.file.abs_src_path].meta["extra_html"], content]
        )

    def on_post_page(self, output, **kwargs):  # This is needed for holoviews.
        return output.replace('.js" defer></script>', '.js"></script>')

    def on_serve(self, server, **kwargs):  # pragma: no cover
        watcher = server.watcher
        builder = list(watcher._tasks.values())[0]["func"]
        root = os.path.join(os.path.dirname(pheasant.__file__), "theme")
        server.watch(root, builder)

        return server

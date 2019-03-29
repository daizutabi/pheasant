import logging
import os

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

        if "extra_css" not in self.config:
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

        config["extra_css"] = list(self.config["extra_css"])
        config["extra_javascript"] = list(self.config["extra_javascript"])

        for file in files_:
            files.append(file)
            path = file.src_path.replace("\\", "/")
            if path.endswith(".css"):
                config["extra_css"].insert(0, path)
            else:
                config["extra_javascript"].insert(0, path)  # pragma: no cover

        return files

    def on_nav(self, nav, config, **kwargs):
        def message(msg):
            logger.info(f"[Pheasant] {msg}".replace(config["docs_dir"], ""))

        paths = [page.file.abs_src_path for page in nav.pages]
        logger.info(f"[Pheasant] Converting {len(paths)} pages.")
        self.converter.convert_from_files(paths, message=message)
        func_time = self.converter.convert_from_files.func_time
        kernel_time = self.converter.convert_from_files.kernel_time
        time = f" (total: {func_time}, kernel: {kernel_time})"
        msg = "Conversion finished:" + " " * 32 + f"{time} "
        message(msg)

        return nav

    def on_page_read_source(self, source, page, **kwargs):
        return self.converter.pages[page.file.abs_src_path].output

    def on_page_content(self, content, page, **kwargs):
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

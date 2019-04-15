import io
import logging
import os
import re
from typing import List

import yaml
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import get_files
from mkdocs.utils import markdown_extensions

import pheasant
from pheasant.core.pheasant import Pheasant

logger = logging.getLogger("mkdocs")

markdown_extensions.append(".py")


class PheasantPlugin(BasePlugin):
    config_scheme = (("jupyter", config_options.Type(bool, default=True)),)
    converter = Pheasant()
    version = pheasant.__version__
    logger.info(f"[Pheasant] Converter created.")

    def on_config(self, config, **kwargs):
        if self.config:
            self.converter.update_config(self.config)
        if not self.config["jupyter"]:
            self.converter.jupyter.death = True

        self.config["extra_css"] = config["extra_css"]
        self.config["extra_javascript"] = config["extra_javascript"]

        logger.info(f"[Pheasant] Converter configured.")

        config["nav"] = build_nav(config["nav"], config["docs_dir"])
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

        for file in files:
            normalize_file(file, config)

        return files

    def on_nav(self, nav, config, **kwargs):
        def message(msg):
            logger.info(f"[Pheasant] {msg}".replace(config["docs_dir"], ""))

        skipped = any(page.title.endswith("*") for page in nav.pages)
        if skipped:
            pages = []
            for page in nav.pages:
                if not page.title.endswith("*"):
                    message(f"Skip conversion: {page.file.abs_src_path}.")
                else:
                    page.title = page.title[:-1]
                    pages.append(page)
        else:
            pages = nav.pages

        paths = [page.file.abs_src_path for page in pages]

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
            return "Skipped."

    def on_page_content(self, content, page, **kwargs):
        if page.file.abs_src_path not in self.converter.pages:
            return content
        else:
            extra = self.converter.pages[page.file.abs_src_path].meta["extra_html"]
            return "\n".join([extra, content])

    def on_post_page(self, output, **kwargs):  # This is needed for holoviews.
        return output.replace('.js" defer></script>', '.js"></script>')

    def on_serve(self, server, **kwargs):  # pragma: no cover
        watcher = server.watcher
        builder = list(watcher._tasks.values())[0]["func"]
        root = os.path.join(os.path.dirname(pheasant.__file__), "theme")
        server.watch(root, builder)
        watcher.ignore_dirs('.pheasant_cache')

        return server


def build_nav(nav: List, docs_dir: str, parent: str = "") -> List:
    for index, entry in enumerate(nav):
        if not isinstance(entry, dict):
            entry = {entry: entry}
            nav[index] = entry
        for key, value in entry.items():
            if isinstance(value, str):
                path = os.path.join(docs_dir, value)
                if os.path.isdir(path):
                    nav_ = []
                    for path in os.listdir(path):
                        # if path == "index.md":
                        #     continue
                        abs_path = os.path.join(docs_dir, value, path)
                        title = get_title(abs_path)
                        nav_.append({title: os.path.join(value, path)})
                    entry[key] = build_nav(nav_, docs_dir, os.path.join(parent, value))
    return nav


def get_title(path):
    if os.path.isdir(path):
        return _get_title(os.path.join(path, "index.md"))
    else:
        return _get_title(path)


TITLE_PATTERN = re.compile(r"^# +#?!? ?(.*)")


def _get_title(path):
    if os.path.exists(path):
        content = read_file(path).strip()
        match = TITLE_PATTERN.match(content)
        if match:
            return match.group(1)
    else:
        title = os.path.basename(os.path.dirname(path))
        match = re.match(r"\w*[0-9]+[._ ](.*)", title)
        if match:
            return match.group(1)
        else:
            return title


def read_file(path):
    with io.open(path, "r", encoding="utf-8-sig", errors="strict") as f:
        return f.readline()


NORMALIZE_PATTERN = re.compile(r"(^|[\\/])\w*[0-9]+[._ ](.*?)")


def normalize_file(file, config):
    if file.dest_path.endswith(".html"):
        file.dest_path = NORMALIZE_PATTERN.sub(r"\1\2", file.dest_path)
        file.dest_path = file.dest_path.replace(" ", "_")
        file.abs_dest_path = os.path.normpath(
            os.path.join(config["site_dir"], file.dest_path)
        )
        file.url = NORMALIZE_PATTERN.sub(r"\1\2", file.url)
        file.url = file.url.replace(" ", "_")

import importlib
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
    config_scheme = (
        ("jupyter", config_options.Type(bool, default=True)),
        ("nav_number", config_options.Type(bool, default=False)),
        ("dirty", config_options.Type(bool, default=True)),
        ("version", config_options.Type(str, default="")),
        ("header", config_options.Type(dict, default={})),  # for backward-compatibility
    )
    converter = Pheasant()
    logger.info("[Pheasant] Converter created.")

    def on_config(self, config):
        self.converter.jupyter.set_config(enabled=self.config["jupyter"])
        numbering = self.config['nav_number']
        if 'disabled' in self.config['header'] and self.config['header']['disabled']:
            numbering = False
        self.converter.header.set_config(numbering=numbering)

        if self.config["version"]:
            try:
                module = importlib.import_module(self.config["version"])
                version = module.__version__
            except Exception:
                version = self.config["version"]
            config["theme"].version = version

        self.config["extra_css"] = list(config["extra_css"])
        self.config["extra_javascript"] = list(config["extra_javascript"])

        logger.info("[Pheasant] Converter configured.")

        if config["nav"]:
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
        css = [x for x in css if x not in self.config["extra_css"]]
        js = [x for x in js if x not in self.config["extra_javascript"]]
        config["extra_css"] = css + self.config["extra_css"]
        config["extra_javascript"] = js + self.config["extra_javascript"]

        for file in files:
            normalize_file(file, config)

        return files

    def on_nav(self, nav, config, files):
        paths = [page.file.abs_src_path for page in nav.pages]
        logger.info(f"[Pheasant] Converting {len(paths)} pages.")
        self.converter.convert_from_files(paths)
        logger.info(f"[Pheasant] Conversion finished. {self.converter.log.info}")
        return nav

    def on_page_read_source(self, page, config):
        try:
            return self.converter.pages[page.file.abs_src_path].source
        except KeyError:
            return "Skipped."

    def on_page_content(self, html, page, config, files):
        if page.toc.items:
            page.title = page.toc.items[0].title
        if page.file.abs_src_path not in self.converter.pages:
            return html
        else:
            extra = self.converter.pages[page.file.abs_src_path].meta["extra_html"]
            return "\n".join([extra, html])

    def on_post_page(self, output, page, config):  # This is needed for holoviews.
        return output.replace('.js" defer></script>', '.js"></script>')

    def on_serve(self, server, config):
        self.converter.dirty = self.config["dirty"]
        watcher = server.watcher
        builder = list(watcher._tasks.values())[0]["func"]
        root = os.path.join(os.path.dirname(pheasant.__file__), "theme")
        server.watch(root, builder)
        watcher.ignore_dirs(".pheasant_cache")

        return server


def build_nav(nav: List, docs_dir: str, parent: str = "") -> List:
    del_entries = []
    for index, entry in enumerate(nav):
        if not isinstance(entry, dict):
            entry = {entry: entry}
            nav[index] = entry
        for key, value in entry.items():
            if not isinstance(value, str):
                continue
            path = os.path.join(docs_dir, value)
            if not os.path.isdir(path):
                continue
            nav_ = []
            for path in os.listdir(path):
                if path == ".pheasant_cache":
                    continue
                abs_path = os.path.join(docs_dir, value, path)
                if os.path.isdir(abs_path):
                    title = get_title_from_dir(abs_path)
                else:
                    ext = os.path.splitext(path)[1]
                    if ext not in markdown_extensions:
                        continue
                    title = get_title_from_file(abs_path)
                nav_.append({title: os.path.join(value, path)})
            if nav_:
                entry[key] = build_nav(nav_, docs_dir, os.path.join(parent, value))
            else:
                del_entries.append(entry)
    for entry in del_entries:
        nav.remove(entry)
    return nav


TITLE_PATTERN = re.compile(r"^# +#?!? ?(.*)")


def get_title_from_file(path):
    content = read_file(path).strip()
    match = TITLE_PATTERN.match(content)
    if match:
        return match.group(1)


def get_title_from_dir(path):
    title = os.path.basename(path).replace("_", " ")
    match = re.match(r"\w*[0-9]+[. ](.*)", title)
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

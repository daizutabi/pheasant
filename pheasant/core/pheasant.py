import os
from dataclasses import field
from typing import Dict, List

from pheasant.core.converter import Converter
from pheasant.core.decorator import Decorator, monitor
from pheasant.core.page import Page
from pheasant.renderers.embed.embed import Embed
from pheasant.renderers.jupyter.jupyter import Jupyter
from pheasant.renderers.number.number import Anchor, Header
from pheasant.renderers.script.script import Script


class Pheasant(Converter):
    script: Script = field(default_factory=Script, init=False)
    jupyter: Jupyter = field(default_factory=Jupyter, init=False)
    header: Header = field(default_factory=Header, init=False)
    embed: Embed = field(default_factory=Embed, init=False)
    anchor: Anchor = field(default_factory=Anchor, init=False)
    decorator: Decorator = field(default_factory=Decorator, init=False)
    pages: Dict[str, Page] = field(default_factory=dict, init=False)

    def init(self):
        self.anchor.header = self.header
        self.register("script", [self.script])
        self.register("main", [self.header, self.jupyter, self.embed])
        self.register("link", [self.anchor])

        self.decorator.name = "pheasant"
        self.decorator.register("surround", [self.header, self.jupyter, self.embed])

    @monitor(format=True)
    def convert_from_files(self, paths: List[str], message=None) -> List[str]:
        common = os.path.commonpath(paths)
        if message:
            message("Converter resetting...")
        self.reset()
        if message:
            message("Done. Start conversion of each page.")
        for path in paths:
            self.jupyter.abs_src_path = path  # for cache and extra resources
            self.header.abs_src_path = path  # for hypyerlink between pages
            self.jupyter.reset()  # Reset cell number for every page
            if path.endswith(".py"):
                self.convert_from_file(path, ["script", "main"])
            else:
                self.convert_from_file(path, "main")
            self.pages[path].meta["extra_html"] = self.jupyter.extra_html
            if message:
                if common:
                    path = path.replace(common, "")[1:]
                path = path.replace("\\", "/")
                func_time = self.convert_from_file.func_time
                kernel_time = self.convert_from_file.kernel_time
                time = f" (total: {func_time}, kernel: {kernel_time})"
                msg = f"Converted: {path:40s} {time} "
                message(msg)

        for path in paths:
            self.anchor.abs_src_path = path
            self.convert_from_output(path, "link")

        return [self.pages[path].output for path in paths]

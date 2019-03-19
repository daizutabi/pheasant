from dataclasses import field
from typing import Any, Dict, List, Optional

from pheasant.code.renderer import Code
from pheasant.core.converter import Converter
from pheasant.core.decorator import Decorator
from pheasant.core.page import Page
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Anchor, Header
from pheasant.python.renderer import Python


class Pheasant(Converter):
    python: Python = field(default_factory=Python, init=False)
    jupyter: Jupyter = field(default_factory=Jupyter, init=False)
    header: Header = field(default_factory=Header, init=False)
    code: Code = field(default_factory=Code, init=False)
    anchor: Anchor = field(default_factory=Anchor, init=False)
    pages: List[Page] = field(default_factory=list)
    decorator: Decorator = field(default_factory=Decorator)

    def __post_init__(self):
        super().__post_init__()
        self.anchor.header = self.header
        self.register("script", [self.python])
        self.register("main", [self.jupyter, self.header, self.code], self.decorator)
        self.register("link", [self.anchor])

        self.decorator.register(self.header, self.decorate_header)

    def init(self, config: Optional[Dict[str, Any]] = None):
        for renderer in self.renderers:
            name = renderer.name
            if config and name in config:
                renderer._update("config", config[name])
            renderer.init()

    def decorate_header(self, output):
        print('xx')

pheasant = Pheasant()
pheasant.convert('hello', "main")



def main():
    pass
    # def on_page_markdown(self, markdown, page, config, files):
    #     logger.info(f"[Pheasant] on_page_markdown: {page.file.src_path}")
    #     # print(markdown)
    #     # page.file.abs_src_path
    #     markdown = self.converter("numbered")(markdown)
    #     # print(markdown)
    #     return markdown
    #
    # def on_page_content(self, content, page, config, files):
    #     logger.info(f"[Pheasant] on_page_content: {page.file.src_path}")
    #     # print(content)
    #     content = self.converter("postprocess")(content)
    #     # print(content)
    #     return content
    #
    # def on_page_context(self, context, page, config, nav):
    #     logger.info(f"[Pheasant] on_page_context: {page.file.src_path}")
    #     extra_resources = self.jupyter.config["extra_resources"]
    #     print(extra_resources)
    #     print(config)
    #     # for key in ['extra_css']:
    #     #     config.context[key].extend(extra_resources[key])
    #     #     print('----------------------------------------------')
    #     #     print(context[key])
    #     # return context
    #     config["pheasant"] = extra_resources
    #
    #     self.jupyter.reset()
    #     # update_page_config(config, page.file.abs_src_path)
    #     return context

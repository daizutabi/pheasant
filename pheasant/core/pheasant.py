from dataclasses import field
from typing import Any, Dict, Optional

from pheasant.code.renderer import Code
from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Anchor, Header
from pheasant.python.renderer import Python


class Pheasant(Converter):
    python: Python = field(default_factory=Python)
    jupyter: Jupyter = field(default_factory=Jupyter)
    header: Header = field(default_factory=Header)
    code: Code = field(default_factory=Code)
    anchor: Anchor = field(default_factory=Anchor)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.anchor.header = self.header
        self.register("script", [self.python])
        self.register("main", [self.jupyter, self.header, self.code])
        self.register("link", [self.anchor])

    def init(self, config: Optional[Dict[str, Any]] = None):
        for renderer in self.renderers:
            name = renderer.name
            if config and name in config:
                renderer.update_config(config[name])
            renderer.init()

    def on_page_markdown(self, markdown, page, config, files):
        logger.info(f"[Pheasant] on_page_markdown: {page.file.src_path}")
        # print(markdown)
        # page.file.abs_src_path
        markdown = self.converter("numbered")(markdown)
        # print(markdown)
        return markdown

    def on_page_content(self, content, page, config, files):
        logger.info(f"[Pheasant] on_page_content: {page.file.src_path}")
        # print(content)
        content = self.converter("postprocess")(content)
        # print(content)
        return content

    def on_page_context(self, context, page, config, nav):
        logger.info(f"[Pheasant] on_page_context: {page.file.src_path}")
        extra_resources = self.jupyter.config["extra_resources"]
        print(extra_resources)
        print(config)
        # for key in ['extra_css']:
        #     config.context[key].extend(extra_resources[key])
        #     print('----------------------------------------------')
        #     print(context[key])
        # return context
        config["pheasant"] = extra_resources

        self.jupyter.reset()
        # update_page_config(config, page.file.abs_src_path)
        return context

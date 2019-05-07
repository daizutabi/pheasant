from dataclasses import field
from typing import Dict, Iterable, List

from pheasant.core.converter import Converter, Page
from pheasant.core.decorator import Decorator
from pheasant.renderers.embed.embed import Embed
from pheasant.renderers.jupyter.jupyter import CacheMismatchError, Jupyter
from pheasant.renderers.jupyter.kernel import kernels
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
    shutdown: bool = False
    restart: bool = False
    verbose: int = 0  # 0: no info, 1: output, 2: code and output

    def init(self):
        self.anchor.header = self.header
        self.register([self.script], "script")
        self.register([self.header, self.jupyter, self.embed], "main")
        self.register([self.anchor], "link")

        self.decorator.name = "pheasant"
        self.decorator.register([self.header, self.jupyter, self.embed], "surround")

        self.jupyter.set_config(verbose=self.verbose)

    def _convert(self, path: str) -> str:
        """Convert a source file with pheasant's parsers except 'link' parser.

        Parameters
        ----------
        path
            The source path to be converted.

        Returns
        -------
        Converted output text.
        """
        if path.endswith(".py"):
            self.convert_by_name(path, "script")
        try:
            return self.convert_by_name(path, "main")
        except CacheMismatchError:
            return self.convert_by_name(path, "main")

    def _convert_from_files(self, paths: Iterable[str]) -> List[str]:
        paths = list(paths)
        self.start()
        self.jupyter.progress_bar.multi = len(paths)
        for k, path in enumerate(paths):
            self.jupyter.progress_bar.step = k + 1
            self.convert(path)

            if self.shutdown:
                kernels.shutdown()
            elif self.restart:
                kernels.restart()

        for path in paths:
            self.convert_by_name(path, "link")

        return [self.pages[path].source for path in paths]

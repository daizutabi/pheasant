import datetime
from contextlib import contextmanager
from dataclasses import field
from typing import Dict, Iterable, List

from pheasant.core.converter import Converter, Page
from pheasant.core.decorator import Decorator
from pheasant.renderers.embed.embed import Embed
from pheasant.renderers.jupyter.jupyter import CacheMismatchError, Jupyter
from pheasant.renderers.jupyter.kernel import kernels
from pheasant.renderers.number.number import Anchor, Header
from pheasant.renderers.script.script import Script
from pheasant.utils.time import format_timedelta_human


class Log:
    pass


class Pheasant(Converter):
    script: Script = field(default_factory=Script, init=False)
    jupyter: Jupyter = field(default_factory=Jupyter, init=False)
    header: Header = field(default_factory=Header, init=False)
    embed: Embed = field(default_factory=Embed, init=False)
    anchor: Anchor = field(default_factory=Anchor, init=False)
    decorator: Decorator = field(default_factory=Decorator, init=False)
    pages: Dict[str, Page] = field(default_factory=dict, init=False)
    log: Log = field(default_factory=Log, init=False)
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

        self.jupyter.verbose = self.verbose

    def _convert_from_files(self, paths: Iterable[str]) -> List[str]:
        paths = list(paths)
        self.start()
        self.jupyter.progress_bar.step = 1
        self.jupyter.progress_bar.multi = len(paths)
        for k, path in enumerate(paths):
            if path.endswith(".py"):
                self.convert(path, "script")
            try:
                self.convert(path, "main")
            except CacheMismatchError:
                self.convert(path, "main")

            if self.shutdown:
                kernels.shutdown()
            elif self.restart:
                kernels.restart()

        for path in paths:
            self.convert(path, "link")

        return [self.pages[path].source for path in paths]

    def convert_from_files(self, paths: Iterable[str]) -> List[str]:
        with elapsed_time(self.log):
            return self._convert_from_files(paths)


@contextmanager
def elapsed_time(log):
    log.start = datetime.datetime.now()
    try:
        yield
    finally:
        log.end = datetime.datetime.now()
        log.elapsed = log.end - log.start
        time = format_timedelta_human(log.elapsed)
        log.info = f"Elapsed time: {time}"

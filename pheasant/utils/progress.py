import datetime
import math
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Union

import colorama
from termcolor import colored

colorama.init()


@dataclass
class ProgressBar:
    multi: int = 0
    step: int = 1
    total: int = 0
    count: int = 0
    bar: str = ""
    status: str = ""
    init: str = ""
    text: str = ""
    parent: Any = None

    def update(self, text: str):
        self.bar = bar(self.step, self.multi, self.count, self.total, self.status, text)
        self.parent.update(self)

    def start(self, text: str = "", count: Optional[int] = 0) -> None:
        self.status = "start"
        if count is not None:
            self.count = count
        self.update(text or self.init)

    def progress(
        self,
        func: Union[Callable[[], Any], str],
        format: Optional[Callable[[Any], str]] = None,
        count: Optional[int] = None,
    ) -> Any:
        if not self.total:
            if callable(func):
                return func()
            else:
                return func

        if not self.status:
            self.start(count=count)

        if isinstance(func, str):
            result = func
        else:
            result = self.parent.supervisor(self, func)

        self.count = count or self.count + 1
        self.text = format(result) if format else result
        self.update(self.text)
        return result

    def finish(
        self, text: str = "", count: Optional[int] = None, done: bool = True
    ) -> None:
        if self.status == "start" or self.status == "skip":
            self.count = count or self.count
            self.status = "done" if done else "skip"
            self.update(text or self.text)
            self.status = ""
            self.count = 0
        if self.multi and done:
            self.step += 1


class Buffer:
    def __init__(self, stream):
        self.stream = stream
        self.on_bar = True
        self.new_line = False

    def write(self, s):
        if self.on_bar and s:
            s = "\n" + s
            self.on_bar = False
        self.new_line = s.endswith("\n")
        return self.stream.write(s)

    def flush(self):
        self.stream.flush()


@dataclass
class ProgressBarManager:
    progress_bars: List[ProgressBar] = field(default_factory=list)
    current: Optional[ProgressBar] = None

    def __post_init__(self):
        self.write = sys.stdout.write
        self.flush = sys.stdout.flush
        self.stream = Buffer(sys.stdout)

    def get_progress_bar(self, total: int = 0, multi: int = 0, init: str = ""):
        progress_bar = ProgressBar(total=total, multi=multi, init=init, parent=self)
        self.progress_bars.append(progress_bar)
        return progress_bar

    def supervisor(self, progress_bar, func):
        with redirect_stdout(self.stream):
            with redirect_stderr(self.stream):
                result = func()
        return result

    def update(self, progress_bar):
        if self.current:
            if self.current != progress_bar:
                self.current.finish(done=False)
            elif self.stream.on_bar:
                length = len(self.current.bar)
                self.write("\r" + " " * length + "\r")
            elif not self.stream.new_line:
                self.write("\n")
            else:
                self.stream.new_line = False

        self.write(progress_bar.bar)
        self.flush()
        self.stream.on_bar = True

        if progress_bar.status == "done" or progress_bar.status == "skip":
            self.write("\n")
            self.flush()

        self.current = progress_bar


progress_bar_manager = ProgressBarManager()


def progress_bar_factory(total: int = 0, multi: int = 0, init: str = ""):
    return progress_bar_manager.get_progress_bar(total=total, multi=multi, init=init)


BAR_LENGTH = 24
ZFILL = 2


def bar(step: int, multi: int, count: int, total: int, status: str, text: str) -> str:

    zfill = max(ZFILL, int(math.log10(total)))
    count_str = str(count).zfill(zfill)
    total_str = str(total).zfill(zfill)
    prefix = colored(f"[{count_str}/{total_str}]", "cyan")

    if count == total:
        color = "green"
        bar = colored("[" + "=" * (BAR_LENGTH + 1) + "]", color)
    else:
        color = "green" if status == "done" else "yellow"
        ratio = min(count / total, 1)
        current = int(BAR_LENGTH * ratio)
        left = colored("[" + "=" * current + ">", "green")
        right = colored(" " * (BAR_LENGTH - current) + "]", color)
        bar = left + right

    if multi:
        fill = int(math.log10(multi))
        step_str = str(step).zfill(fill)
        multi_str = str(multi).zfill(fill)
        prefix_multi = f" [{step_str}/{multi_str}]"
        prefix_multi = colored(prefix_multi, "green" if multi == step else "yellow")
    else:
        prefix_multi = " "

    if text:
        text = colored(text, color)

    datetime_format = r" %H:%M:%S "
    now = datetime.datetime.now().strftime(datetime_format)

    return "".join([prefix, bar, prefix_multi, text, now])

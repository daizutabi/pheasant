import datetime
import io
import itertools
import sys
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Union

import colorama
from termcolor import colored

from pheasant.utils.time import format_timedelta_human

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

    def write(self, s):
        if s:
            if self.on_bar:
                s = "\n" + s
                self.on_bar = False
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
        self.stdout = Buffer(sys.stdout)
        self.stderr = Buffer(sys.stderr)

    def get_progress_bar(self, total: int = 0, multi: int = 0, init: str = ""):
        progress_bar = ProgressBar(total=total, multi=multi, init=init, parent=self)
        self.progress_bars.append(progress_bar)
        return progress_bar

    def supervisor(self, progress_bar, func):
        with redirect_stdout(self.stdout):
            with redirect_stderr(self.stderr):
                result = func()
        return result

    def update(self, progress_bar):
        if self.current:
            if self.current != progress_bar:
                self.current.finish(done=False)
            else:
                length = len(self.current.bar)
                self.write("\r" + " " * length + "\r")
                self.flush()

        self.write(progress_bar.bar)
        self.flush()
        if progress_bar.status == "done" or progress_bar.status == "skip":
            self.write("\n")
            self.flush()
            self.stdout.on_bar = False
            self.stderr.on_bar = False
        else:
            self.stdout.on_bar = True
            self.stderr.on_bar = True
        self.current = progress_bar


progress_bar_manager = ProgressBarManager()


def progress_bar_factory(total: int = 0, multi: int = 0, init: str = ""):
    return progress_bar_manager.get_progress_bar(total=total, multi=multi, init=init)


def prefix(step: int, multi: int, count: int, total: int, zfill: int = 3) -> str:
    if multi > 1:
        step_str = str(step).zfill(zfill)
        multi_str = str(multi).zfill(zfill)
        prefix = f"({step_str}/{multi_str}) "
    elif multi == 1:
        prefix = " " * (zfill * 2 + 4)
    else:
        prefix = ""

    count_str = str(count).zfill(zfill)
    total_str = str(total).zfill(zfill)
    return prefix + colored(f"[{count_str}/{total_str}]", "cyan")


def bar(
    step: int,
    multi: int,
    count: int,
    total: int,
    status: str,
    text: str = "",
    zfill: int = 3,
    bar_length: int = 30,
) -> str:
    if count == total:
        color = "green"
        bar = colored("[" + "=" * (bar_length + 1) + "]", color)
    else:
        color = "green" if status == "done" else "yellow"
        ratio = min(count / total, 1)
        current = int(bar_length * ratio)
        left = colored("[" + "=" * current + ">", "green")
        right = colored(" " * (bar_length - current) + "]", color)
        bar = left + right
    if text:
        bar += colored(" " + text, color)
    return " ".join([prefix(step, multi, count, total, zfill), bar])


def main():
    from pheasant.renderers.jupyter.kernel import Kernel, output_hook_factory

    kernel = Kernel("python3")
    kernel.start(silent=False)
    kernel.execute("import time")

    def callback(stream, data):
        sys.stdout.write(data)

    output_hook = output_hook_factory(callback)

    def run():
        kernel.execute(
            "time.sleep(1)\nprint(11)\ntime.sleep(1)\nprint(22)\ntime.sleep(1)",
            output_hook=output_hook,
        )
        time.sleep(0.2)
        print(1)
        time.sleep(0.1)
        print(2)
        time.sleep(0.1)
        print(3)
        time.sleep(0.2)

        return str(datetime.datetime.now())

    bar = progress_bar_factory(total=3, multi=3, init="start...")
    for k in range(3):
        for k in range(bar.total):
            bar.progress(run)
        bar.finish()


if __name__ == "__main__":
    main()

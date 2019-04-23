import datetime
import itertools
import sys
import threading
import time

import colorama
import cursor
from termcolor import colored

from pheasant.utils.time import format_timedelta_human

colorama.init()


class ProgressBar:
    def __init__(
        self, total: int = 0, multi: int = 0, spinner: bool = True, init: str = ""
    ):
        self.total = total
        self.multi = multi
        self.step = 1
        self.spinner = spinner
        self.init = init
        self.count = 0
        self.bar_length = 30
        self.zfill = 3
        self.write = sys.stdout.write
        self.flush = sys.stdout.flush
        self.bar = ""
        self.show = False
        self.result = ""

    def spin(self, done):
        start = datetime.datetime.now()
        limit = datetime.timedelta(seconds=1)
        status = ""
        for char in itertools.cycle("|/-\\"):
            dt = datetime.datetime.now() - start
            if dt > limit:
                status = " " + char + " " + format_timedelta_human(dt)
                self.write(status)
                self.flush()
                self.write("\x08" * len(status))
            if done.wait(0.3):
                break
        self.write(" " * len(status) + "\x08" * len(status))

    def supervisor(self, func):
        done = threading.Event()
        spinner = threading.Thread(target=self.spin, args=(done,))
        spinner.start()
        try:
            result = func()
        finally:
            done.set()
        spinner.join()
        return result

    def update(self, result=None, finish=False):
        count = str(self.count).zfill(self.zfill)
        total = str(self.total).zfill(self.zfill)
        prefix = f"[{count}/{total}]"
        prefix = colored(prefix, "cyan")

        if self.multi > 1:
            step = str(self.step).zfill(self.zfill)
            multi = str(self.multi).zfill(self.zfill)
            prefix = f"({step}/{multi}) " + prefix
        elif self.multi == 1:
            prefix = " " * 10 + prefix

        if self.count == self.total:
            color = "green"
            bar = colored("[" + "=" * self.bar_length + "=]", color)
        else:
            color = "green" if finish else "yellow"
            current = int(self.bar_length * min(self.count / self.total, 1))
            bar = (
                colored("[", "green")
                + colored("=" * current, "green")
                + colored(">", "green", attrs=["bold"])
                + colored("." * (self.bar_length - current), color)
                + colored("]", color)
            )

        bar = " ".join([prefix, bar])
        if result:
            bar = " ".join([bar, colored(result, color)])
            self.result = result
        back = "\x08" * len(self.bar)
        self.write(back + bar)
        self.flush()
        diff = len(self.bar) - len(bar)
        if diff > 0:
            self.write(" " * diff + "\x08" * diff)
            self.flush()
        self.bar = bar
        self.show = True

    def progress(self, func, format=None, count=None, init=None):
        if not self.total:
            if callable(func):
                return func()
            else:
                return func

        if self.count == 0:
            cursor.hide()
            self.update(init or self.init)

        if isinstance(func, str):
            result = func
        elif self.spinner:
            result = self.supervisor(func)
        else:
            result = func()

        self.count = count or self.count + 1
        self.update(result if not format else format(result))

        return result

    def finish(self, count=None, reset=True, finish=True):
        if count:
            self.count = count
        if self.show:
            self.update(self.result, finish=finish)
            self.write("\n")
            self.flush()
            self.show = False
            cursor.show()
        if reset:
            self.count = 0
        if self.multi and finish:
            self.step += 1


def main():
    def run():
        time.sleep(0.5)
        sys.stderr.write("ERROR\n")
        sys.stderr.flush()
        time.sleep(1)
        return "hello"

    bar = ProgressBar(3, multi=3)
    for k in range(3):
        for k in range(bar.total):
            bar.progress(run, init="start..........")
        bar.finish()


if __name__ == "__main__":
    main()

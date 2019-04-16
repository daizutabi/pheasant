import datetime
import itertools
import sys
import threading
import time

import colorama
import cursor
from termcolor import colored

from pheasant.core.base import format_timedelta

colorama.init()


class ProgressBar:
    def __init__(self, total: int = 0, spinner: bool = True, init: str = ""):
        self.total = total
        self.spinner = spinner
        self.init = init
        self.count = 0
        self.bar_length = 50
        self.zfill = 4
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
                status = " " + char + " " + format_timedelta(dt)
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
        result = func()
        done.set()
        spinner.join()
        return result

    def update(self, result=None, finish=False):
        count = str(self.count).zfill(self.zfill)
        total = str(self.total).zfill(self.zfill)
        prefix = f"[{count}/{total}]"
        prefix = colored(prefix, "cyan", attrs=["bold"])

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
                + colored("-" * (self.bar_length - current), color)
                + colored("]", color)
            )

        bar = " ".join([prefix, bar])
        if result:
            bar = " ".join([bar, colored(result, color)])
            self.result = result
        back = "\x08" * len(self.bar)
        self.write(back + bar)
        diff = len(self.bar) - len(bar)
        if diff > 0:
            self.write(" " * diff + "\x08" * diff)
        self.bar = bar
        self.show = True

    def progress(self, func, format=None, init=None):
        if self.count == 0:
            cursor.hide()
            self.update(init or self.init)

        if self.spinner:
            result = self.supervisor(func)
        else:
            result = func()

        self.count += 1
        self.update(result if not format else format(result))

        return result

    def finish(self):
        if self.show:
            self.update(self.result, finish=True)
            self.write("\n")
            self.flush()
            cursor.show()
            self.show = False


def main():
    def run():
        time.sleep(2)
        return "hello"

    progress_bar = ProgressBar(3)
    for k in range(3):
        for k in range(progress_bar.total):
            progress_bar.progress(run, init="start..........")
        progress_bar.finish()


if __name__ == "__main__":
    main()

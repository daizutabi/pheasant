"""Jupyter Kernel"""
import ast
import atexit
import datetime
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from jupyter_client.client import KernelClient
from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
from jupyter_client.manager import KernelManager

from pheasant.utils.progress import progress_bar_factory
from pheasant.utils.time import format_timedelta_human


@dataclass
class Kernel:
    name: str
    init_code: str = ""
    language: str = ""
    manager: Optional[KernelManager] = field(default=None, init=False)
    client: Optional[KernelClient] = field(default=None, init=False)
    report: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.report["total"] = datetime.timedelta(0)
        kernel_spec = get_kernel_spec(self.name)
        self.language = kernel_spec.language
        if self.language == "python":
            self.init_code = (
                "from pheasant.renderers.jupyter.ipython import register_formatters\n"
                "register_formatters()"
            )

        def shutdown():  # pragma: no cover
            if self.manager:
                print(f"Shutting down kernel [{self.name}]...", end="")
                self.manager.shutdown_kernel()
                print("Done.")

        atexit.register(shutdown)

    def start(self, timeout=10, silent=True) -> KernelClient:
        if self.manager:
            if self.manager.is_alive():
                return self.client
            else:  # pragma: no cover
                raise RuntimeError(f"Kernel {self.name} is not alive.")

        def start():
            self.manager = KernelManager(kernel_name=self.name)
            self.manager.start_kernel()
            self.client = self.manager.blocking_client()
            self.client.start_channels()
            try:
                self.client.wait_for_ready(timeout=timeout)
            except TimeoutError:  # pragma: no cover
                self.manager.shutdown_kernel()
                return False
            else:
                self.client.execute_interactive(self.init_code)
                return self.client

        init = f"Starting kernel [{self.name}]"
        progress_bar = progress_bar_factory(total=3, init=init)
        now = datetime.datetime.now()

        def message(result):
            dt = format_timedelta_human(datetime.datetime.now() - now)
            return f"Kernel [{self.name}] started ({dt})" if result else "Retrying..."

        for k in range(progress_bar.total):
            if silent and start():
                break
            elif silent:
                continue
            elif progress_bar.progress(start, message):
                progress_bar.finish()
                break
        else:
            raise TimeoutError  # pragma: no cover
        return self.client

    def shutdown(self) -> None:
        if self.manager:
            self.manager.shutdown_kernel()
            del self.client
            self.client = None
            del self.manager
            self.manager = None

    def restart(self) -> None:
        if self.manager:
            self.manager.restart_kernel()
            if self.client and self.init_code:
                self.client.execute_interactive(self.init_code)

    def execute(self, code: str, output_hook=None) -> List:
        client = self.client or self.start()
        outputs = []

        def _output_hook(msg):
            if output_hook:
                output_hook(msg)
            output = output_from_msg(msg)
            if output:
                outputs.append(output)

        msg = client.execute_interactive(code, output_hook=_output_hook)
        update_report(self.report, msg)
        return list(stream_joiner(outputs))

    def inspect(self, code: str, output_hook=None) -> List:
        self.execute("import inspect")
        self.execute(code, output_hook=output_hook)
        outputs = self.execute(CODE_FOR_INSPECT)
        if len(outputs) == 1 and outputs[0]["type"] == "execute_result":
            source = ast.literal_eval(outputs[0]["data"]["text/plain"])
            return [dict(type="stream", name="source", text=source)]
        else:
            return outputs


CODE_FOR_INSPECT = """
def getsource(obj):
    if hasattr(obj, '__dataclass_params__'):
        is_dataclass = True
    else:
        is_dataclass = False
    source = inspect.getsource(obj)
    defaults = [('init', True), ('repr', True), ('eq', True), ('order', False),
                ('unsafe_hash', False), ('frozen', False)]
    if is_dataclass and not source.startswith('@dataclass'):
        args = []
        params = obj.__dataclass_params__
        if params.init is False:
            args.append('init=False')
        if params.repr is False:
            args.append('repr=False')
        if params.eq is False:
            args.append('eq=False')
        if params.order is True:
            args.append('order=True')
        if params.unsafe_hash is True:
            args.append('unsafe_hash=True')
        if params.frozen is True:
            args.append('frozen=True')
        if args:
            args = "(" + ", ".join(args) + ")"
        else:
            args = ""
        source = f"@dataclass{args}\\n{source}"
    return source
getsource(_)
"""


@dataclass
class Kernels:
    _kernel_names: Dict[str, list] = field(default_factory=dict)
    kernels: Dict[str, Kernel] = field(default_factory=dict)

    @property
    def kernel_names(self) -> Dict[str, list]:
        """Kernel name dictionary for languages. """
        if self._kernel_names:
            return self._kernel_names
        kernel_specs = find_kernel_specs()
        for kernel_name in kernel_specs:
            kernel_spec = get_kernel_spec(kernel_name)
            language = kernel_spec.language
            if language not in self._kernel_names:
                self._kernel_names[language] = [kernel_name]
            else:
                self._kernel_names[language].append(kernel_name)
        return self._kernel_names

    def get_kernel_name(self, language: str, index: int = 0) -> str:
        """Select one kernel name for a language."""
        if language not in self.kernel_names:
            return ""
        else:
            return self.kernel_names[language][index]

    def get_kernel(self, kernel_name: str) -> Kernel:
        if kernel_name not in self.kernels:
            self.kernels[kernel_name] = Kernel(kernel_name)
        return self.kernels[kernel_name]

    def __getitem__(self, language: str) -> Kernel:
        kernel_name = self.get_kernel_name(language)
        if not kernel_name:
            raise KeyError(f"No kernel found for language {language}.")
        return self.get_kernel(kernel_name)

    def shutdown(self):
        for kernel_name in list(self.kernels.keys()):
            kernel = self.kernels.pop(kernel_name)
            kernel.shutdown()

    def restart(self):
        for kernel in self.kernels.values():
            kernel.restart()


kernels = Kernels()


def update_report(report: Dict[str, Any], msg: Dict[str, Any]) -> None:
    start = msg["parent_header"]["date"].astimezone()
    end = msg["header"]["date"].astimezone()
    report["start"] = start
    report["end"] = end
    report["time"] = end - start
    report["total"] += report["time"]


def format_report(report: Dict[str, Any]):
    report = dict(report)
    if "start" not in report:
        return {}
    datetime_format = r"%Y-%m-%d %H:%M:%S"
    report["start"] = report["start"].strftime(datetime_format)
    report["end"] = report["end"].strftime(datetime_format)
    report["time"] = format_timedelta_human(report["time"])
    report["total"] = format_timedelta_human(report["total"])
    return report


def output_from_msg(msg: Dict[str, Any]) -> Optional[dict]:
    """Create an output dictionary from a kernel's IOPub message.

    Returns
    -------
    dict: the output as a dictionary.
    """
    msg_type = msg["msg_type"]
    content = msg["content"]

    if msg_type == "execute_result":
        return dict(type=msg_type, data=content["data"], metadata=content["metadata"])
    elif msg_type == "display_data":
        return dict(type=msg_type, data=content["data"], metadata=content["metadata"])
    elif msg_type == "stream":
        return dict(type=msg_type, name=content["name"], text=content["text"])
    elif msg_type == "error":
        traceback = "\n".join([strip_ansi(tr) for tr in content["traceback"][1:-1]])
        if content["ename"] == "NameError":
            raise NameError(content["evalue"])
        return dict(
            type=msg_type,
            ename=content["ename"],
            evalue=content["evalue"],
            traceback=traceback.strip(),
        )
    else:
        return None


def stream_joiner(outputs: List[Dict]) -> Iterator[Dict]:
    name = text = ""
    for output in outputs:
        if output["type"] != "stream":
            if text:
                yield stream_cell(name, text)
                name = text = ""
            yield output
            continue
        if not name:
            name = output["name"]
        if output["name"] == name:
            text += output["text"]
        else:
            yield stream_cell(name, text)
            name, text = output["name"], output["text"]
    if text:
        yield stream_cell(name, text)


def stream_cell(name: str, text: str) -> Dict[str, str]:
    if "\x08" in text:
        text, source = "", text
        index = 0
        for char in source:
            if char == "\x08":
                text = text[:-1]
            elif char == "\r":
                text = text[:index]
            elif char == "\n":
                text += char
                index = len(text)
            else:
                text += char
    return {"type": "stream", "name": name, "text": text.rstrip()}


# from nbconvert.filters.ansi
_ANSI_RE = re.compile("\x1b\\[(.*?)([@-~])")


def strip_ansi(source: str) -> str:
    """
    Remove ANSI escape codes from text.

    Parameters
    ----------
    source
        Source to remove the ANSI from
    """
    return _ANSI_RE.sub("", source)


def output_hook_factory(callback=None):
    if callback is None:

        def callback(stream, data):
            if stream == "stdout":
                sys.stdout.write(data)
            else:
                sys.stderr.write(data)

    def output_hook_default(msg):
        msg_type = msg["header"]["msg_type"]
        content = msg["content"]
        if msg_type == "stream":
            callback(content["name"], content["text"])
        elif msg_type in ("display_data", "execute_result"):
            data = content["data"].get("text/plain")
            if data:
                callback("stdout", data)
        elif msg_type == "error":
            callback("stderr", "\n".join(content["traceback"]))

    return output_hook_default


output_hook = output_hook_factory()

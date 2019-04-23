import atexit
import datetime
import re
from typing import Any, Dict, Iterator, List, Optional

from jupyter_client.kernelspec import find_kernel_specs, get_kernel_spec
from jupyter_client.manager import KernelManager
from jupyter_client.client import KernelClient
from pheasant.utils.progress import ProgressBar
from pheasant.utils.time import format_timedelta_human

from dataclasses import dataclass, field


@dataclass
class Kernel:
    name: str
    manager: Optional[KernelManager] = field(default=None, init=False)
    client: Optional[KernelClient] = field(default=None, init=False)
    report: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.report["total"] = datetime.timedelta(0)

    def start(self, init_code="", timeout=3, retry=10, silent=True) -> KernelClient:
        if self.manager:
            if self.manager.is_alive():
                return self.client
            else:
                raise RuntimeError(f"Kernel {self.name} is not alive.")

        def start():
            self.manager = KernelManager(kernel_name=self.name)
            self.manager.start_kernel()
            self.client = self.manager.blocking_client()
            self.client.start_channels()
            try:
                self.client.execute_interactive(init_code, timeout=timeout)
            except TimeoutError:
                self.manager.shutdown_kernel()
                return False
            else:
                atexit.register(self.manager.shutdown_kernel)
                return self.client

        init = f"Starting kernel [{self.name}]"
        progress_bar = ProgressBar(retry, init=init, multi=1)
        now = datetime.datetime.now()

        def message(result):
            dt = format_timedelta_human(datetime.datetime.now() - now)
            return f"Kernel [{self.name}] started ({dt})" if result else "Retrying..."

        for k in range(retry):
            if silent and start():
                break
            elif silent:
                continue
            elif progress_bar.progress(start, message):
                progress_bar.finish()
                break
        else:
            raise TimeoutError
        return self.client

    def shutdown(self) -> None:
        if self.manager:
            atexit.unregister(self.manager.shutdown_kernel)
            self.manager.shutdown_kernel()
            del self.client
            self.client = None
            del self.manager
            self.manager = None

    def execute(self, code: str) -> List:
        client = self.client or self.start()
        outputs = []

        def output_hook(msg):
            # print(msg)
            output = output_from_msg(msg)
            if output:
                outputs.append(output)

        msg = client.execute_interactive(code, output_hook=output_hook)
        update_report(self.report, msg)
        return list(stream_joiner(outputs))


@dataclass
class Kernels:
    _kernel_names: Dict[str, list] = field(default_factory=dict)
    kernels: Dict[str, Kernel] = field(default_factory=dict)
    report: Dict[str, Any] = field(default_factory=dict)
    language: str = "python"

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

    def execute(self, code: str, kernel_name: str = "", language: str = "") -> List:
        language = language or self.language
        kernel_name = kernel_name or self.get_kernel_name(language)
        if not kernel_name:
            raise ValueError(f"No kernel found for language {language}.")
        kernel = self.get_kernel(kernel_name)
        outputs = kernel.execute(code)
        self.language = language
        self.report = kernel.report
        return outputs


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
        return dict(type=msg_type, data=content["data"])
    elif msg_type == "display_data":
        return dict(type=msg_type, data=content["data"])
    elif msg_type == "stream":
        return dict(type=msg_type, name=content["name"], text=content["text"])
    elif msg_type == "error":
        traceback = "\n".join([strip_ansi(tr) for tr in content["traceback"][1:-1]])
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
    return {"type": "stream", "name": name, "text": text.strip()}


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

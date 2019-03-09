"""A module provides jupyter client interface."""
import atexit
import logging
import re
from typing import Any, Dict, List, Optional

import jupyter_client
from jupyter_client.manager import KernelManager

from pheasant.jupyter.config import config

logger = logging.getLogger("mkdocs")

kernel_names: Dict[str, list] = {}
kernel_managers: Dict[str, Any] = {}
kernel_clients: Dict[str, Any] = {}


def find_kernel_names() -> Dict[str, list]:
    """Find kernel names for languages.

    Returns
    -------
    kernel_names
        dict of {language: list of kernel name}.
    """
    if kernel_names:
        return kernel_names

    kernel_specs = jupyter_client.kernelspec.find_kernel_specs()
    for kernel_name in kernel_specs:
        kernel_spec = jupyter_client.kernelspec.get_kernel_spec(kernel_name)
        language = kernel_spec.language
        if language not in kernel_names:
            kernel_names[language] = [kernel_name]
        else:
            kernel_names[language].append(kernel_name)

    return kernel_names


def select_kernel_name(language: str) -> Optional[str]:
    """Select one kernel name for a language."""
    if language in config["kernel_name"]:
        return config["kernel_name"][language]

    kernel_names = find_kernel_names()
    if language not in kernel_names:
        config["kernel_name"][language] = None
        return None

    kernel_name = kernel_names[language][0]
    config["kernel_name"][language] = kernel_name
    if len(kernel_names[language]) > 1:
        logger.warning(f"Multiple kernels are found for {language}.")
        logger.warning(f'Use kernel_name "{kernel_name}" for {language}.')
    return kernel_name


def get_kernel_manager(kernel_name: str) -> KernelManager:
    if kernel_name in kernel_managers:
        return kernel_managers[kernel_name]

    logger.info(f'[Pheasant] Creating kernel manager for "{kernel_name}".')
    kernel_manager = jupyter_client.KernelManager(kernel_name=kernel_name)

    logger.info(f'[Pheasant] Starting kernel: "{kernel_name}".')
    kernel_manager.start_kernel()

    def shutdown_kernel():
        logger.info(f'[Pheasant] Shutting down kernel: "{kernel_name}".')
        kernel_manager.shutdown_kernel()

    atexit.register(shutdown_kernel)
    kernel_managers[kernel_name] = kernel_manager
    return kernel_manager


def get_kernel_client(kernel_name: str):
    if kernel_name in kernel_clients:
        return kernel_clients[kernel_name]

    logger.info(f'[Pheasant] Creating kernel client for "{kernel_name}".')
    kernel_manager = get_kernel_manager(kernel_name)
    kernel_client = kernel_manager.client()
    kernel_client.start_channels()
    logger.info(f"[Pheasant] Kernel client ready: {kernel_name}.")
    kernel_clients[kernel_name] = kernel_client
    return kernel_client


executed = [False]


def execute(
    code: str, kernel_name: Optional[str] = None, language: str = "python"
) -> List[Dict[str, Any]]:
    if kernel_name is None:
        kernel_name = select_kernel_name(language)
        if kernel_name is None:
            raise ValueError(f"No kernel found for language {language}.")

    kernel_client = get_kernel_client(kernel_name)

    outputs = []

    def output_hook(msg):
        output = output_from_msg(msg)
        if output:
            outputs.append(output)

    if not executed[0]:
        logger.info(f'[Pheasant] First execution started for "{kernel_name}".')

    kernel_client.execute_interactive(code, allow_stdin=False, output_hook=output_hook)

    if not executed[0]:
        executed[0] = True
        logger.info(f'[Pheasant] First execution ended for "{kernel_name}".')

    return outputs


def output_from_msg(msg) -> Optional[dict]:
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
        traceback = [strip_ansi(tr) for tr in content["traceback"]]
        return dict(
            type=msg_type,
            ename=content["ename"],
            evalue=content["evalue"],
            traceback=traceback,
        )
    else:
        return None


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

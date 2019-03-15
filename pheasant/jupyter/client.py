"""A module provides jupyter client interface."""
import atexit
import logging
from typing import Any, Dict, List, Optional

import jupyter_client
from jupyter_client import KernelManager

logger = logging.getLogger(__name__)

kernel_names: Dict[str, list] = {}
kernel_managers: Dict[str, Any] = {}


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


def get_kernel_name(language: str, index: int = 0) -> Optional[str]:
    """Select one kernel name for a language."""
    kernel_names = find_kernel_names()
    if language not in kernel_names:
        return None
    else:
        return kernel_names[language][index]


def get_kernel_manager(kernel_name: str) -> KernelManager:
    if kernel_name in kernel_managers:
        kernel_manager = kernel_managers[kernel_name]

        if not kernel_manager.is_alive():
            if not kernel_manager.has_kernel:
                kernel_manager.restart_kernel()
                logger.info(f'Restarting kernel: "{kernel_name}".')
            else:
                kernel_manager.start_kernel()
                logger.info(f'Starting kernel: "{kernel_name}".')
    else:
        logger.info(f'Creating kernel manager: "{kernel_name}".')
        kernel_manager = KernelManager(kernel_name=kernel_name)
        logger.info(f'Starting kernel: "{kernel_name}".')
        kernel_manager.start_kernel()

        def shutdown_kernel():
            logger.info(f'Shutting down kernel: "{kernel_name}".')
            kernel_manager.shutdown_kernel()

        atexit.register(shutdown_kernel)
        kernel_managers[kernel_name] = kernel_manager

    if not kernel_manager.is_alive():
        raise ValueError(f'Kernel could not start: "{kernel_name}".')
    else:
        return kernel_manager


def execute(
    code: str,
    kernel_name: Optional[str] = None,
    language: str = "python",
    kernel_manager: KernelManager = None,
) -> List[Dict[str, Any]]:
    if kernel_manager is None:
        if kernel_name is None:
            kernel_name = get_kernel_name(language)
            if kernel_name is None:
                raise ValueError(f"No kernel found for language {language}.")

        kernel_manager = get_kernel_manager(kernel_name)
    kernel_client = kernel_manager.client()

    outputs = []

    def output_hook(msg):
        output = output_from_msg(msg)
        if output:
            outputs.append(output)

    kernel_client.execute_interactive(code, allow_stdin=False, output_hook=output_hook)

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
        return dict(type=msg_type, name=content["name"], text=content["text"].strip())
    elif msg_type == "error":
        return dict(type=msg_type, ename=content["ename"], evalue=content["evalue"])
    else:
        return None

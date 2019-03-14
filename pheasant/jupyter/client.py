"""A module provides jupyter client interface."""
import atexit
import logging
from typing import Any, Dict, List, Optional

import jupyter_client
from jupyter_client.manager import KernelManager

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

    logger.info(f"[Pheasant.jupyter] Finding Kernel names.")
    kernel_specs = jupyter_client.kernelspec.find_kernel_specs()
    for kernel_name in kernel_specs:
        kernel_spec = jupyter_client.kernelspec.get_kernel_spec(kernel_name)
        language = kernel_spec.language
        if language not in kernel_names:
            kernel_names[language] = [kernel_name]
        else:
            kernel_names[language].append(kernel_name)

    logger.info(f"[Pheasant.jupyter] Found kernels: {kernel_names}.")

    return kernel_names


def select_kernel_name(language: str) -> Optional[str]:
    """Select one kernel name for a language."""
    kernel_names = find_kernel_names()
    if language not in kernel_names:
        return None
    kernel_name = kernel_names[language][0]
    if len(kernel_names[language]) > 1:
        logger.warning(f"Multiple kernels are found for {language}.")
        logger.warning(f'Use kernel_name "{kernel_name}" for {language}.')
    return kernel_name


def get_kernel_manager(kernel_name: str) -> KernelManager:
    if kernel_name in kernel_managers:
        kernel_manager = kernel_managers[kernel_name]
        if not kernel_manager.is_alive():
            logger.info(f'[Pheasant.jupyter] Restarting kernel: "{kernel_name}".')
            kernel_manager.start_kernel()
        return kernel_manager

    logger.info(f'[Pheasant.jupyter] Creating kernel manager for "{kernel_name}".')
    kernel_manager = jupyter_client.KernelManager(kernel_name=kernel_name)

    logger.info(f'[Pheasant.jupyter] Starting kernel "{kernel_name}".')
    kernel_manager.start_kernel()

    def shutdown_kernel():
        logger.info(f'[Pheasant.jupyter] Shutting down kernel: "{kernel_name}".')
        kernel_manager.shutdown_kernel()

    atexit.register(shutdown_kernel)
    kernel_managers[kernel_name] = kernel_manager
    return kernel_manager


def get_kernel_client(kernel_name: str):
    if kernel_name in kernel_clients:
        return kernel_clients[kernel_name]

    kernel_manager = get_kernel_manager(kernel_name)
    logger.info(f'[Pheasant.jupyter] Creating kernel client for "{kernel_name}".')
    kernel_client = kernel_manager.client()
    kernel_client.start_channels()
    while not kernel_client.is_complete('print("OK")'):
        pass
    logger.info(f'[Pheasant.jupyter] Kernel client for "{kernel_name}" ready.')
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

    kernel_manager = get_kernel_manager(kernel_name)
    if not kernel_manager.is_alive():
        kernel_manager.start_kernel()
    kernel_client = kernel_manager.client()
    kernel_client.start_channels()

    # kernel_client = get_kernel_client(kernel_name)

    outputs = []

    def output_hook(msg):
        output = output_from_msg(msg)
        if output:
            outputs.append(output)

    if not executed[0]:
        logger.info(f'[Pheasant.jupyter] First execution started for "{kernel_name}".')

    kernel_client.execute_interactive(code, allow_stdin=False, output_hook=output_hook)

    if not executed[0]:
        executed[0] = True
        logger.info(f'[Pheasant.jupyter] First execution ended for "{kernel_name}".')

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
        return dict(
            type=msg_type,
            ename=content["ename"],
            evalue=content["evalue"],
        )
    else:
        return None

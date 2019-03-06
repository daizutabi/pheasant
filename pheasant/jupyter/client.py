"""A module provides jupyter client interface."""

import atexit
import logging
from queue import Empty
from typing import Any, Dict, Optional, Union

import jupyter_client
import nbformat
from jupyter_client.manager import KernelManager
from nbformat import NotebookNode
from nbformat.v4 import output_from_msg

from pheasant.jupyter.config import config

logger = logging.getLogger('mkdocs')

kernel_names: Dict[str, list] = {}
kernel_managers: Dict[str, Any] = {}
kernel_clients: Dict[str, Any] = {}


def find_kernel_names() -> Dict[str, list]:
    """Find kernel names for languages."""
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
    if language in config['kernel_name']:
        return config['kernel_name'][language]

    kernel_names = find_kernel_names()
    if language not in kernel_names:
        config['kernel_name'][language] = None
        return None

    kernel_name = kernel_names[language][0]
    config['kernel_name'][language] = kernel_name
    if len(kernel_names[language]) > 1:
        logger.warning(f'Multiple kernels are found for {language}.')
        logger.warning(f'Use kernel_name `{kernel_name}` for {language}.')
    return kernel_name


def get_kernel_manager(kernel_name: str) -> KernelManager:
    if kernel_name in kernel_managers:
        kernel_manager = kernel_managers[kernel_name]
    else:
        kernel_specs = jupyter_client.kernelspec.find_kernel_specs()
        if kernel_name not in kernel_specs:
            msg = f'Could not find kernel name: {kernel_name}'
            raise ValueError(msg)
        logger.info(f'[Pheasant] Creating kernel manager'
                    f' for kernel: {kernel_name}')
        kernel_manager = jupyter_client.KernelManager(kernel_name=kernel_name)
        kernel_managers[kernel_name] = kernel_manager
        atexit.register(shutdown_kernels)

    if not kernel_manager.is_alive():
        kernel_manager.start_kernel()

    return kernel_manager


def get_kernel_client(kernel_name: str):
    kernel_manager = get_kernel_manager(kernel_name)
    if kernel_name in kernel_clients:
        return kernel_clients[kernel_name]
    else:
        logger.info(f'[Pheasant] Creating kernel client'
                    f' for kernel: {kernel_name}')
        if not kernel_manager.is_alive():
            kernel_manager.start_kernel()
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        # try:
        #     kernel_client.wait_for_ready(timeout=60)
        # except RuntimeError:
        #     logger.error(f"[Pheasant] Kernel can't start: {kernel_name}")
        #     kernel_client.stop_channels()
        #     kernel_manager.shutdown_kernel()

        logger.info(f'[Pheasant] Kernel client ready: {kernel_name}')
        kernel_client.allow_stdin = False
        kernel_clients[kernel_name] = kernel_client
        return kernel_client


def _wait_for_reply(kernel_name: str, msg_id, timeout: int = 300):
    # wait for finish, with timeout
    kernel_client = get_kernel_client(kernel_name)
    while True:
        try:
            msg = kernel_client.shell_channel.get_msg(timeout=timeout)
        except Empty:
            logger.error("Timeout waiting for execute reply (%is)." % timeout)
            logger.error("Interrupting kernel")
            kernel_manager = get_kernel_manager(kernel_name)
            kernel_manager.interrupt_kernel()
            break

        if msg['parent_header'].get('msg_id') == msg_id:
            return msg
        else:
            # not our reply
            continue


def run_cell(cell_or_source: Union[NotebookNode, str],
             kernel_name: Optional[str] = None,
             language: str = 'python') -> Optional[NotebookNode]:
    if isinstance(cell_or_source, str):
        return_cell = True
        cell = nbformat.v4.new_code_cell(cell_or_source)
    else:
        return_cell = False
        cell = cell_or_source

    if kernel_name is None:
        if ('pheasant' in cell.metadata
                and 'kernel_name' in cell.metadata['pheasant']):
            kernel_name = cell.metadata['pheasant']['kernel_name']
        else:
            kernel_name = select_kernel_name(language=language)
            kernel_name = config.setdefault('default_kernel', kernel_name)

    if not isinstance(kernel_name, str):
        raise ValueError('No kernel')

    kernel_client = get_kernel_client(kernel_name)
    msg_id = kernel_client.execute(cell.source)
    # logger.debug(f'Executing cell:\n{cell.source}')
    _wait_for_reply(kernel_name, msg_id)

    outs = cell.outputs = []

    while True:
        try:
            # We've already waited for execute_reply, so all output
            # should already be waiting. However, on slow networks, like
            # in certain CI systems, waiting < 1 second might miss messages.
            # So long as the kernel sends a status:idle message when it
            # finishes, we won't actually have to wait this long, anyway.
            msg = kernel_client.iopub_channel.get_msg(timeout=50)
        except Empty:
            logger.warn('Timeout waiting for IOPub output')
            raise RuntimeError('Timeout waiting for IOPub output')

        if msg['parent_header'].get('msg_id') != msg_id:
            # not an output from our execution
            continue

        msg_type = msg['msg_type']
        # logger.debug(f'output: {msg_type}')
        content = msg['content']

        # set the prompt number for the input and the output
        if 'execution_count' in content:
            cell['execution_count'] = content['execution_count']

        if msg_type == 'status':
            if content['execution_state'] == 'idle':
                break
            else:
                continue
        elif msg_type == 'execute_input':
            continue
        elif msg_type == 'clear_output':
            outs[:] = []
            continue
        elif msg_type.startswith('comm'):
            continue
        elif msg_type == 'update_display_data':
            continue

        try:
            out = output_from_msg(msg)
        except ValueError:
            logger.error("Unhandled iopub msg: " + msg_type)
            continue

        outs.append(out)

    cell.outputs = outs

    return cell if return_cell else None


def shutdown_kernels() -> None:
    for kernel_name in kernel_managers:
        logger.info(f'[Pheasant] Shutting down kernel: {kernel_name}')
        kernel_manager = kernel_managers[kernel_name]
        kernel_manager.shutdown_kernel()

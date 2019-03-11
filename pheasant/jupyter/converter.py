import os
import re
from typing import Iterator

from jinja2 import Environment, FileSystemLoader

from pheasant.jupyter.client import execute
from pheasant.jupyter.config import config
from pheasant.jupyter.preprocess import (preprocess_fenced_code,
                                         preprocess_markdown)
from pheasant.jupyter.renderer import (execute_and_render, render_fenced_code,
                                       render_inline_code)
from pheasant.markdown.splitter import fenced_code_splitter


def initialize() -> None:
    config["INLINE_PATTERN"] = re.compile(config["inline_pattern"])
    set_template()
    insert_extra_paths()
    import_extra_modules()
    run_init_codes()


def convert(source: str) -> str:
    """Convert markdown string into markdown with running results.

    Parameters
    ----------
    source : str
        Markdown source string.

    Returns
    -------
    results : str
        Markdown source with running results
    """
    reload_extra_modules()

    config["run_counter"] = 0  # used in the cache module. MOVE!!
    return "".join(code_runner(source))


def code_runner(source: str) -> Iterator[str]:
    """Generate markdown string with outputs after running the source.

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    str
        Markdown string.
    """
    for splitted in fenced_code_splitter(source):
        if isinstance(splitted, str):
            cmd = "<!-- break -->"
            if cmd in splitted:
                splitted = splitted[: splitted.index(cmd)]
                yield preprocess_markdown(splitted)
                break
            else:
                yield preprocess_markdown(splitted)
        else:
            language, code, options = splitted
            if "inline" in options:
                code = preprocess_fenced_code(code)
                if "hide" in options:
                    execute(code, language=language)
                else:
                    yield execute_and_render(
                        code, render_inline_code, language=language, options=options
                    ) + "\n\n"
            else:
                yield execute_and_render(
                    code, render_fenced_code, language=language, options=options
                )


def set_template() -> None:
    default_directory = os.path.join(os.path.dirname(__file__), "templates")
    for prefix in ["fenced_code", "inline_code"]:
        abspath = os.path.abspath(config[prefix + "_template_file"])
        template_directory, template_file = os.path.split(abspath)
        loader = FileSystemLoader([template_directory, default_directory])
        env = Environment(loader=loader, autoescape=False)
        config[prefix + "_template"] = env.get_template(template_file)


def insert_extra_paths() -> None:
    code = (
        f"import sys\n"
        f'for path in {config["extra_paths"]}:\n'
        f"    if path not in sys.path:\n"
        f"        sys.path.insert(0, path)\n"
    )
    execute(code)


def import_extra_modules() -> None:
    modules = ", ".join(
        config["extra_modules"] + ["pheasant.jupyter.display", "importlib", "inspect"]
    )
    execute(f"import {modules}")


def run_init_codes() -> None:
    execute("import pandas\npandas.options.display.max_colwidth = 0")
    execute("\n".join(config["init_codes"]))


def reload_extra_modules() -> None:
    for module in config["extra_modules"]:
        execute("importlib.reload(pandas)")

import logging
import os
import re
from typing import Any, Dict, Iterable, Match, Optional

from jinja2 import Environment, FileSystemLoader

from pheasant.core.converter import Client
from pheasant.jupyter.kernel import execute
from pheasant.jupyter.renderer import (execute_and_render, replace,
                                       update_extra_resources)
from pheasant.number.config import config as number_config

logger = logging.getLogger("mkdocs")


BACKQUOTE_CODE_PATTERN = (
    r"^(?P<pre>`{3,})(?P<language>\S*)" r"(?P<option>.*?)\n(?P<code>.*?)\n(?P=pre)\n"
)

TILDE_CODE_PATTEN = (
    r"^(?P<pre>~{3,})(?P<language>\S*)" r"(?P<option>.*?)\n(?P<code>.*?)\n(?P=pre)\n"
)

INLINE_CODE_PATTERN = r"\{\{(?P<code>.+?)\}\}"
HEADER_INLINE_CODE_PATTERN = r"^(?P<pre>#[^\n.]+)\{\{(?P<code>.+?)\}\}(?P<post>.*?)$"


class Jupyter(Client):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("jupyter", config)
        self.register("tilde", TILDE_CODE_PATTEN, self.tilde_code)
        self.register("backquote", BACKQUOTE_CODE_PATTERN, self.backqoute_code)
        self.register(
            "header_inline", HEADER_INLINE_CODE_PATTERN, self.header_inline_code
        )
        self.register("inline", INLINE_CODE_PATTERN, self.inline_code)

        self.set_template()
        self.insert_extra_paths()
        self.import_extra_modules()
        self.run_init_codes()

    def backqoute_code(self, context: Dict[str, str]) -> Iterable[str]:
        if "inline" in context["option"]:

            def replace_(match: Match) -> str:
                return replace(match.group("code"), ignore_equal=True)

            context["code"] = re.sub(INLINE_CODE_PATTERN, replace_, context["code"])

            if "hide" in context["option"]:
                execute(context["code"], language=context["language"])
            else:
                yield execute_and_render(
                    self.config["inline_code_template"].render, strip=True, **context
                )
        else:
            yield execute_and_render(
                self.config["fenced_code_template"].render, **context
            )

    def tilde_code(self, context: Dict[str, str]) -> Iterable[str]:
        context["language"] = context["language"] or "markdown"
        escaped_backquotes = '<span class="pheasant-backquote">```</span>'
        context["code"] = context["code"].replace("```", escaped_backquotes)
        yield self.config["escaped_code_template"].render(**context)

    def inline_code(self, context: Dict[str, str]) -> Iterable[str]:
        code = context["code"]
        if code.startswith(self.config["inline_ignore_character"]):
            yield "{{" + code[1:] + "}}"
            return

        if code.startswith(self.config["inline_display_character"]):
            display = True
            code = code[1:]
        else:
            display = False

        code = replace(code, self.config["inline_html_character"])
        yield execute_and_render(
            self.config["inline_code_template"].render,
            code=code,
            language="python",
            callback=update_extra_resources,
            display=display,
            strip=True,
        )

    def header_inline_code(self, context: Dict[str, str]) -> Iterable[str]:
        print('HERE', context)
        source = "\n".join(
            [
                context["pre"] + context["post"],
                number_config["begin_pattern"],
                *self.inline_code(context),
                number_config["end_pattern"],
            ]
        )
        yield from self.renderer.parse(source)

    def set_template(self) -> None:
        default_directory = os.path.join(os.path.dirname(__file__), "templates")
        for prefix in ["fenced_code", "inline_code", "escaped_code"]:
            if prefix + "_template" in self.config:
                continue
            abspath = os.path.abspath(self.config[prefix + "_template_file"])
            logger.info(f'[Pheasant.jupyter] Template path "{abspath}" for {prefix}.')
            template_directory, template_file = os.path.split(abspath)
            loader = FileSystemLoader([template_directory, default_directory])
            env = Environment(loader=loader, autoescape=False)
            self.config[prefix + "_template"] = env.get_template(template_file)

    def insert_extra_paths(self) -> None:
        if not self.config["extra_paths"]:
            return

        code = (
            f"import sys\n"
            f'for path in {self.config["extra_paths"]}:\n'
            f"    if path not in sys.path:\n"
            f"        sys.path.insert(0, path)\n"
        )
        logger.info(
            f'[Pheasant.jupyter] Extra paths added: {self.config["extra_paths"]}.'
        )
        execute(code)

    def import_extra_modules(self) -> None:
        modules = ", ".join(
            self.config["extra_modules"]
            + ["pheasant.jupyter.display", "importlib", "inspect"]
        )
        execute(f"import {modules}")
        if self.config["extra_modules"]:
            names = f'{self.config["extra_modules"]}'
            logger.info(f"[Pheasant.jupyter] Extra modules imported: {names}.")

    def run_init_codes(self) -> None:
        execute("import pandas\npandas.options.display.max_colwidth = 0")
        if self.config["init_codes"]:
            execute("\n".join(self.config["init_codes"]))
            logger.info(
                f'[Pheasant.jupyter] Init codes executed: {self.config["init_codes"]}.'
            )

    def reload_extra_modules(self) -> None:
        for module in self.config["extra_modules"]:
            execute(f"importlib.reload({module})")

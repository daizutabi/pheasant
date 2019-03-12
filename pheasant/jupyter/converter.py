import logging
import os
from typing import Any, Dict, Iterator, Match, Optional

from jinja2 import Environment, FileSystemLoader

from pheasant.core.converter import Converter, History
from pheasant.jupyter.client import execute
from pheasant.jupyter.preprocess import replace, update_extra_resources
from pheasant.jupyter.renderer import execute_and_render, strip_text
from pheasant.markdown.config import (BACKQUOTE_CODE_PATTERN,
                                      INLINE_CODE_PATTERN, TILDE_CODE_PATTEN)

logger = logging.getLogger("mkdocs")


class Jupyter(Converter):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("jupyter", config)
        self.register("tilde", TILDE_CODE_PATTEN, self.convert_tilde_code)
        self.register("backquote", BACKQUOTE_CODE_PATTERN, self.convert_backqoute_code)
        self.register("inline", INLINE_CODE_PATTERN, self.convert_inline_code)

        self.set_template()
        self.insert_extra_paths()
        self.import_extra_modules()
        self.run_init_codes()

    def convert(self, source: str) -> str:
        self.config["run_counter"] = 0  # used in the cache module. MOVE!!
        return super().convert(source)

    def get_context(self, match: Match):
        prefix, language, option, code = match.groups()
        options = option.strip().split(" ")
        context = dict(prefix=prefix, code=code, language=language, options=options)
        return context

    def convert_backqoute_code(self, match: Match, history: History) -> str:
        if history is None:
            context = self.get_context(match)
            return execute_and_render(self.render_fenced_code, **context)
        else:
            return match.group()

    def convert_tilde_code(self, match: Match, history: History) -> str:
        if history is None:
            context = self.get_context(match)
            context["language"] = context["language"] or "markdown"
            escaped_backquotes = '<span class="pheasant-backquote">```</span>'
            context["code"] = context["code"].replace("```", escaped_backquotes)
            return self.render_escaped_code(context)
        else:
            return match.group()

    def convert_inline_code(self, match: Match, history: History) -> str:
        if history is None:
            code = match.group(1)
            if code.startswith(self.config["inline_ignore_character"]):
                return match.group().replace(code, code[1:])
            elif code.startswith(self.config["inline_display_character"]):
                display = True
                code = code[1:]
            else:
                display = False

            code = replace(code, self.config['inline_html_character'])
            return execute_and_render(
                self.render_inline_code,
                code=code,
                language="python",
                callback=update_extra_resources,
                display=display,
            )
        else:
            return match.group()



    # def code_runner(source: str) -> Iterator[str]:
    #     """Generate markdown string with outputs after running the source.
    #
    #     Parameters
    #     ----------
    #     source : str
    #         Markdown source string.
    #
    #     Yields
    #     ------
    #     str
    #         Markdown string.
    #     """
    #     for splitted in fenced_code_splitter(source):
    #         if isinstance(splitted, str):
    #             cmd = "<!-- break -->"
    #             if cmd in splitted:
    #                 splitted = splitted[: splitted.index(cmd)]
    #                 yield preprocess_markdown(splitted)
    #                 break
    #             else:
    #                 yield preprocess_markdown(splitted)
    #         else:
    #             language, code, options = splitted
    #             if "inline" in options:
    #                 code = preprocess_fenced_code(code)
    #                 if "hide" in options:
    #                     execute(code, language=language)
    #                 else:
    #                     yield execute_and_render(
    #                         code, render_inline_code, language=language, options=options
    #                     ) + "\n\n"
    #             else:
    #                 yield execute_and_render(
    #                     code, render_fenced_code, language=language, options=options
    #                 )
    #

    def render_fenced_code(self, context: dict) -> str:
        """Convert a fenced code into markdown or html."""
        return self.config["fenced_code_template"].render(**context)

    def render_escaped_code(self, context: dict) -> str:
        """Convert a fenced code into markdown or html."""
        return self.config["escaped_code_template"].render(**context)

    def render_inline_code(self, context: dict) -> str:
        """Convert an inline code into markdown or html."""
        strip_text(context["outputs"])
        return self.config["inline_code_template"].render(**context)

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

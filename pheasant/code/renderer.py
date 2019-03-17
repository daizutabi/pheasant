import codecs
import os
from ast import literal_eval
from typing import Any, Dict, Iterable, Optional

from pheasant.core.parser import Parser
from pheasant.core.renderer import Config, Context, Renderer
from pheasant.jupyter.client import execute, get_kernel_name


class Code(Renderer):

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>~{3,})(?P<language>\w+) ?(?P<option>.*?)\n"
        r"(?P<source>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"^(?P<header>#?)!\[(?P<language>\w+?)\]\((?P<source>.+?)\)\n"

    def __init__(self, name: str = "", config: Optional[Config] = None):
        super().__init__(name, config)
        self.register(Code.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Code.INLINE_CODE_PATTERN, self.render_inline_code)
        self.set_template("fenced_code")

    def render_fenced_code(self, context: Context, parser: Parser) -> Iterable[str]:
        if context["language"] == "copy":
            context["language"] = "markdown"
            copy = True
        else:
            copy = False
        yield self.render(self.config["fenced_code_template"], context)

        if copy:
            yield "\n"  # important.
            yield from parser.parse(context["source"] + "\n")

    def render_inline_code(self, context: Context, parser: Parser) -> Iterable[str]:
        language = context["language"]
        if context["header"]:
            header = "Code" if language == "python" else "File"
            source = context["source"]
            source = f"#{header} {source}\n![{language}]({source})\n"
            yield from parser.parse(source)
        elif language == "file":
            path = context["source"]
            # path, language, slice_str = resolve_path(path)
            if not os.path.exists(path):
                yield f'<p style="font-color:red">File not found: {path}</p>\n'
            else:
                context["source"] = read_file(path)
                context["language"] = "python"  # FIXME
                yield from self.render_fenced_code(context, parser)
                yield "\n"
        elif language == "python":
            kernel_name = get_kernel_name(language)
            if kernel_name is None:
                yield f'<p style="font-color:red">Kernel not found for {language}</p>\n'
            else:
                context["source"] = inspect(kernel_name, context["source"])
                yield from self.render_fenced_code(context, parser)
                yield "\n"
        else:
            yield f'<p style="font-color:red">{language} not supported</p>\n'

    def render(self, template, context: Dict[str, Any]) -> str:
        context.update(config=self.config)
        return template.render(**context)


def read_file(path):
    with codecs.open(path, "r", "utf8") as file:
        source = file.read()
    return source.replace("\r\n", "\n").replace("\r", "\n").strip()


def inspect(kernel_name: str, obj: str) -> str:
    """Inspect source code."""
    code = f"import inspect\ninspect.getsourcelines({obj})"
    outputs = execute(code, kernel_name=kernel_name)
    # FIXME: when error occurs
    lines, lineno = literal_eval(outputs[0]["data"]["text/plain"])
    return "".join(lines)


# CODE LATER
# def resolve_path(path: str) -> Tuple[str, str, str]:
#     if "?" in path:
#         path, language = path.split("?")
#     else:
#         language = ""
#
#     match = re.match(r"(.+)<(.+?)>", path)
#     if match:
#         path, slice_str = match.groups()
#     else:
#         slice_str = ""
#
#     if not language:
#         ext = os.path.splitext(path)[-1]
#         if ext:
#             ext = ext[1:]  # Remove a dot.
#         language_exts = {"python": ["py"], "yaml": ["yml"]}  # FIXME
#         for language, exts in language_exts.items():
#             if ext in exts:
#                 break
#         else:
#             language = ""
#
#     if slice_str:
#         sources = source.split("\n")
#         if ":" not in slice_str:
#             source = sources[int(slice_str)]
#         else:
#             slice_list = [int(s) if s else None for s in slice_str.split(":")]
#             source = "\n".join(sources[slice(*slice_list)])

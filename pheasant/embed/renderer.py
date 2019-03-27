import os
from ast import literal_eval
from typing import Dict, Iterator, Optional

from pheasant.core import markdown
from pheasant.core.decorator import comment
from pheasant.core.renderer import Renderer
from pheasant.jupyter.client import execute, get_kernel_name


class Embed(Renderer):

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>~{3,})(?P<language>\w*) ?(?P<option>.*?)\n"
        r"(?P<source>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"\{%(?P<source>.+?)%\}"

    def __post_init__(self):
        super().__post_init__()
        self.register(Embed.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Embed.INLINE_CODE_PATTERN, self.render_inline_code)
        self.set_template("fenced_code")

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        if context["language"] == "copy":
            context["language"] = "markdown"
            copy = True
        else:
            if not context["language"]:
                context["language"] = "markdown"
            copy = False
        yield self.render("fenced_code", context) + "\n"

        if copy:
            splitter.send(context["source"] + "\n")

    @comment("source")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        context.update(resolve_path(context["source"].strip()))
        language = context["language"]
        path = context["path"]
        if context["mode"] == "file":
            if not os.path.exists(path):
                yield f'<p style="font-color:red">File not found: {path}</p>\n'
                return
            source = read_file(path)
        else:
            kernel_name = get_kernel_name(language)
            if kernel_name is None:  # pragma: no cover
                yield f'<p style="font-color:red">Kernel not found for {language}</p>\n'
                return
            source = inspect(path, kernel_name)
        source = select_source(source, context.get("lineno"))
        context = {"language": language, "source": source}
        source = f"~~~{language}\n{source}\n~~~\n"
        splitter.send(source)


def resolve_path(path: str) -> Dict[str, str]:
    context = {"mode": "file"}
    if "?" in path and not path.startswith("?"):
        path, context["language"] = path.split("?")
    if "[" in path and ":" in path and path.endswith("]"):
        path, context["lineno"] = path[:-1].split("[")
    if path.startswith("?"):
        context["mode"] = "inspect"
        path = path[1:]
    context["path"] = path
    if "language" not in context:
        context["language"] = get_language_from_path(context["path"])
    return context


def get_language_from_path(path: str) -> str:
    _, ext = os.path.splitext(path)
    if ext in [".py"]:
        return "python"
    elif ext in [".yml"]:
        return "yaml"
    else:
        return "text"


def read_file(path):
    with open(path, "r", encoding="utf-8-sig") as file:
        return file.read().strip()


def inspect(obj: str, kernel_name: str) -> str:
    """Inspect source code."""
    code = f"import inspect\ninspect.getsourcelines({obj})"
    outputs = execute(code, kernel_name=kernel_name)
    try:
        lines, lineno = literal_eval(outputs[0]["data"]["text/plain"])
    except Exception:
        lines = ["inspect error"]
    return "".join(lines)


def select_source(source: str, lineno: str) -> str:
    if not lineno:
        return source
    lines = source.split("\n")
    lineno = lineno[:-1]
    begin_str, end_str = lineno.split(":")
    begin = int(begin_str) if begin_str else 0
    end = int(end_str) if end_str else len(source)
    return "\n".join(lines[begin:end])


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

import os
import re
from ast import literal_eval
from dataclasses import field
from typing import Any, Dict, Iterator

from pheasant.core.decorator import commentable
from pheasant.core.renderer import Renderer
from pheasant.renderers.jupyter.kernel import kernels
from pheasant.renderers.script.script import Script


class Embed(Renderer):
    script: Script = field(default_factory=Script, init=False)

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>~{3,})(?P<language>\w*) ?(?P<option>.*?)\n"
        r"(?P<source>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"\{%(?P<source>.+?)%\}"

    def init(self):
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
        if not context["option"]:
            context["option"] = "source"
        yield "\n" + self.render("fenced_code", context) + "\n\n"

        if copy:
            splitter.send(context["source"] + "\n")

    @commentable("source")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        context.update(resolve_path(context["source"].strip(), self.page.path))
        language = context["language"]
        if context["mode"] in ["file", "include"]:
            path = context["abs_src_path"]
            if not os.path.exists(path):
                yield f'<p style="font-color:red">File not found: {path}</p>\n'
                return
            source = read_file(path)
            if context["mode"] == "include":
                if path.endswith(".py"):
                    source = self.script.parse(source)
                source = shift_header(source, context.get("shift", 0))
        else:
            language = "python"
            kernel_name = kernels.get_kernel_name(language)
            if kernel_name is None:  # pragma: no cover
                yield f'<p style="font-color:red">Kernel not found for {language}</p>\n'
                return
            source = inspect(context["path"], kernel_name)
        source = select_source(source, context.get("lineno"))
        if context["mode"] in ["file", "inspect"]:
            source = f"\n~~~{language} file\n{source}\n~~~\n"
        else:
            source += "\n"
        splitter.send(source)


def resolve_path(path: str, root: str) -> Dict[str, str]:
    context: Dict[str, Any] = {}
    if "?" in path and not path.startswith("?"):
        path, context["language"] = path.split("?")
    if "[" in path and ":" in path and path.endswith("]"):
        path, context["lineno"] = path[:-1].split("[")

    if path.startswith("?"):
        context["mode"] = "inspect"
        path = path[1:]
    elif path.startswith("="):
        context["mode"] = "file"
        path = path[1:]
    else:
        context = {"mode": "include"}
        match = re.match(r"(.+)>(\d)$", path)
        if match:
            path, context["shift"] = match.group(1), int(match.group(2))

    if path.startswith("/"):
        path = path[1:]
        context["abs_src_path"] = os.path.abspath(path)
    else:
        directory = os.path.dirname(root)
        context["abs_src_path"] = os.path.abspath(os.path.join(directory, path))

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

    try:
        outputs = kernels.get_kernel(kernel_name).execute(code)
        lines, lineno = literal_eval(outputs[0]["data"]["text/plain"])
    except Exception:
        lines = ["inspect error"]
    return "".join(lines)


def select_source(source: str, lineno: str) -> str:
    if not lineno:
        return source
    lines = source.split("\n")
    begin_str, end_str = lineno.split(":")
    begin = int(begin_str) if begin_str else 0
    end = int(end_str) if end_str else len(lines)
    return "\n".join(lines[begin:end])


HEADER_PATTERN = re.compile(r"^(#.*?\n)", re.MULTILINE)


def shift_header(source, shift):
    if shift < 1:
        return source
    prefix = "#" * shift
    return HEADER_PATTERN.sub(prefix + r"\1", source)

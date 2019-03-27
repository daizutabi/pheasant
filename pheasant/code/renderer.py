import os
from ast import literal_eval
from typing import Iterator

from pheasant.core import markdown
from pheasant.core.decorator import comment
from pheasant.core.renderer import Renderer
from pheasant.jupyter.client import execute, get_kernel_name


class Code(Renderer):

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>~{3,})(?P<language>\w*) ?(?P<option>.*?)\n"
        r"(?P<source>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"^(?P<header>#?)!\[(?P<language>\w+?)\]\((?P<source>.+?)\)\n"

    def __post_init__(self):
        super().__post_init__()
        self.register(Code.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Code.INLINE_CODE_PATTERN, self.render_inline_code)
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

    @comment("language")
    def render_inline_code(self, context, splitter, parser) -> Iterator[str]:
        language = context["language"]
        if context["header"]:
            header = "Code" if language == "python" else "File"
            source = context["source"]
            source = f"#{header} {source}\n![{language}]({source})\n"
            splitter.send(source)
        elif language == "file":
            path = context["source"]
            if "<" in path:
                path, lineno = path.split("<")
            else:
                lineno = None
            if not os.path.exists(path):
                yield f'<p style="font-color:red">File not found: {path}</p>\n'
            else:
                source = get_source(path, lineno)
                language = get_language_from_path(path)
                source = f"~~~{language}\n{source}\n~~~\n"
                splitter.send(source)
        elif language == "python":
            kernel_name = get_kernel_name(language)
            if kernel_name is None:  # pragma: no cover
                yield f'<p style="font-color:red">Kernel not found for {language}</p>\n'
            else:
                source = inspect(kernel_name, context["source"])
                source = f"~~~{language}\n{source}\n~~~\n"
                splitter.send(source)
        else:
            yield markdown.convert(context["_source"])


def get_source(path, lineno):
    source = read_file(path)
    if not lineno:
        return source
    source = source.split("\n")
    lineno = lineno[:-1]
    begin, end = lineno.split(":")
    begin = int(begin) if begin else 0
    end = int(end) if end else len(source)
    return "\n".join(source[begin:end])


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


def inspect(kernel_name: str, obj: str) -> str:
    """Inspect source code."""
    code = f"import inspect\ninspect.getsourcelines({obj})"
    outputs = execute(code, kernel_name=kernel_name)
    # FIXME: when error occurs
    try:
        lines, lineno = literal_eval(outputs[0]["data"]["text/plain"])
    except Exception:
        lines = ["inspect error"]
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

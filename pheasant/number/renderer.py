import os
import re
from dataclasses import field
from typing import Any, Dict, Iterator, List, Optional, Tuple

from pheasant.core import markdown
from pheasant.core.renderer import Renderer


class Header(Renderer):
    tag_context: Dict[str, Any] = field(default_factory=dict)
    number_list: Dict[str, List[int]] = field(default_factory=dict)
    header_kind: Dict[str, str] = field(default_factory=dict)
    abs_src_path: str = field(default=".")  # should be set the real path later

    HEADER_PATTERN = r"^(?P<prefix>#+)(?P<kind>\w*?) +(?P<title>.+?)\n"
    TAG_PATTERN = r"\{#(?P<tag>\S+?)#\}"
    CONTENT_PATTERN = r"^<!-- *begin *-->\n(?P<content>.*?)\n<!-- *end *-->\n"

    def __post_init__(self):
        super().__post_init__()
        self.register(Header.HEADER_PATTERN, self.render_header)
        self.register(Header.CONTENT_PATTERN, self.render_content)
        self.set_template("header")
        self.config["kind_prefix"] = {}
        self.header_kind[""] = "header"
        for kind in ["figure", "table", "code", "file"]:
            self.header_kind[kind[:3].lower()] = kind
            self.config["kind_prefix"][kind] = kind[0].upper() + kind[1:]
        self.config["kind"] = list(self.header_kind.values())
        self.setup()

    def setup(self):
        self.reset()

    def reset(self) -> None:
        self.reset_number_list()

    def reset_number_list(self) -> None:
        for kind in self.config["kind"]:
            self.number_list[kind] = [0] * 6

    def render_header(self, context, splitter, parser) -> Iterator[str]:
        kind = self.header_kind[context["kind"][:3].lower()]
        depth = len(context["prefix"]) - 1
        self.number_list[kind][depth] += 1
        reset = [0] * (len(self.number_list[kind]) - depth)
        self.number_list[kind][depth + 1 :] = reset
        header = context["prefix"] if kind == "header" else ""
        prefix = self.config["kind_prefix"][kind] if kind != "header" else ""
        number_list = normalize_number_list(self.number_list, kind, depth)
        number_string = number_list_format(number_list)
        title, tag = split_tag(context["title"])
        title, inline_code = split_inline_code(title)

        context_ = {
            "kind": kind,
            "header": header,
            "prefix": prefix,
            "title": title,
            "number_list": number_list,
            "number_string": number_string,
        }

        if tag:
            self.tag_context[tag] = {
                "kind": kind,
                "number_list": number_list,
                "number_string": number_string,
                "abs_src_path": self.abs_src_path,
            }
            context_.update(tag=tag)

        if kind == "header":
            yield self.render("header", context_) + "\n"
        else:
            rest = ""
            if inline_code:
                content = "".join(parser.parse(inline_code))
            else:
                content = ""
                while not content:
                    cell = next(splitter)
                    if cell.match:
                        if cell.source.startswith("~~~") and kind in "figure table":
                            content = cell.context["source"] + "\n"
                            content = markdown.convert(content)
                        else:
                            content = "".join(parser.parse_from_cell(cell, splitter))
                    else:
                        content, rest = self._get_content(cell)
            yield self.render("header", context_, content=content) + "\n"
            splitter.send(rest)

    def render_content(self, context, splitter, parser) -> Iterator[str]:
        content = "".join(parser.parse(context["content"] + "\n", decorate=False))
        yield markdown.convert(content)

    def _get_content(self, cell):
        content = cell.source
        index = content.find("\n\n")
        if index == -1:
            content, rest = content, ""
        else:
            content, rest = content[:index], content[index + 2 :]
        content = markdown.convert(content)
        return content, rest


class Anchor(Renderer):
    header: Optional[Header] = field(default=None)
    abs_src_path: str = field(default=".")  # should be set the real path later

    def __post_init__(self):
        super().__post_init__()
        self.register(Header.TAG_PATTERN, self.render_tag)
        self.set_template("anchor")

    def render_tag(self, context, splitter, parser) -> Iterator[str]:
        if self.header is None:
            raise ValueError("A Header instance has not set yet.")
        tag = context["tag"]

        if context["tag"].startswith("#"):
            yield context["_source"].replace(context["tag"], context["tag"][1:])
        else:
            context = self.resolve(tag)
            yield self.render("anchor", context, reference=True)

    def resolve(self, tag: str) -> Dict[str, Any]:
        tag_context = self.header.tag_context  # type: ignore
        found = tag in tag_context
        if found:
            context = tag_context[tag]
            context["found"] = True
            relpath = os.path.relpath(
                context["abs_src_path"], os.path.dirname(self.abs_src_path)
            )
            relpath = relpath.replace("\\", "/")
            context["ref"] = "#".join([relpath, tag])
        else:
            context = {"found": False, "tag": tag}
        return context


def normalize_number_list(
    number_list: Dict[str, List[int]], kind: str, depth: int
) -> List[int]:
    if kind == "header":
        return number_list[kind][: depth + 1]
    else:
        return number_list["header"][: depth + 1] + [number_list[kind][depth]]


def number_list_format(number_list: List[int]) -> str:
    return ".".join([str(x) for x in number_list])


def split_tag(title: str) -> Tuple[str, str]:
    """Split a tag from `title`. Return (title, tag).

    Parameters
    ----------
    title
        header text

    Returns
    -------
    (title, tag)

    Examples
    --------
    >>> split_tag('{#tag#} text')
    ('text', 'tag')
    >>> split_tag('text')
    ('text', '')
    """
    match = re.search(Header.TAG_PATTERN, title)
    if match:
        return title.replace(match.group(), "").strip(), match.group(1)
    else:
        return title, ""


def split_inline_code(title: str) -> Tuple[str, str]:
    """Split an inline code from `title`. Return (title, inline code).

    Parameters
    ----------
    title
        header text

    Returns
    -------
    (title, inline code)
    """
    from pheasant.jupyter.renderer import Jupyter

    match = re.search(Jupyter.INLINE_CODE_PATTERN, title)
    if match:
        return title.replace(match.group(), "").strip(), match.group()
    else:
        return title, ""

import os
import re
from dataclasses import field
from typing import Any, Dict, Iterator, List, Optional, Tuple

from markdown import Markdown

from pheasant.core.decorator import comment
from pheasant.core.renderer import Renderer


class Header(Renderer):
    tag_context: Dict[str, Any] = field(default_factory=dict)
    number_list: Dict[str, List[int]] = field(default_factory=dict)
    header_kind: Dict[str, str] = field(default_factory=dict)
    abs_src_path: str = "."

    HEADER_PATTERN = r"^(?P<prefix>#+)(?P<kind>\w*) *(?P<title>.*?)\n"
    TAG_PATTERN = r"\{#(?P<tag>\S+?)#\}"

    markdown = Markdown(extensions=["tables"])

    def init(self):
        self.register(Header.HEADER_PATTERN, self.render_header)
        self.set_template("header")
        self.config["kind_prefix"] = {}
        self.header_kind[""] = "header"
        for kind in ["figure", "table", "equation"]:
            self.header_kind[kind[:3].lower()] = kind
            self.config["kind_prefix"][kind] = kind[0].upper() + kind[1:]
        self.header_kind["eq"] = kind
        self.config["kind"] = list(self.header_kind.values())
        self.reset()

    def reset(self) -> None:
        self.meta["ignored_path"] = set()
        self.meta["ignored_depth"] = 100
        for kind in self.config["kind"]:
            self.number_list[kind] = [0] * 6

    def render_header(self, context, splitter, parser) -> Iterator[str]:
        context = self.resolve(context)
        kind = context["kind"]
        if kind == "header":
            if context["inline_pattern"]:
                context["title"] = parser.parse(context["_title"], decorate=False)
            yield self.render("header", context) + "\n\n"
        elif kind == "equation":
            context["content"] = parser.parse(context["_title"], decorate=False)
            yield self.render("header", context) + "\n\n"
        else:
            rest = ""
            if context["inline_pattern"]:
                content = parser.parse(context["inline_pattern"])
            else:
                content = ""
                while not content:
                    cell = next(splitter)
                    if cell.match:
                        content = get_content_from_cell(cell, kind, splitter, parser)
                    else:
                        content, rest = get_content(cell.source)
            yield self.render("header", context, content=content) + "\n\n"
            if rest:
                splitter.send(rest)

    def resolve(self, context):
        kind = context["kind"][:3].lower()
        if kind in self.header_kind:
            kind = self.header_kind[kind]
        else:
            kind = context["kind"]
            if kind not in self.config["kind"]:
                self.config["kind"].append(kind)
                self.number_list[kind] = [0] * 6
                self.config["kind_prefix"][kind] = kind
        depth = len(context["prefix"]) - 1
        title = context["title"]

        numbered = False
        if title.startswith("##"):
            title = title[2:]
            self.meta["ignored_path"].add(self.abs_src_path)
        elif title.startswith("#"):
            title = title[1:]
            self.meta["ignored_depth"] = depth
        elif self.abs_src_path in self.meta["ignored_path"]:
            pass
        elif depth > self.meta["ignored_depth"]:
            pass
        else:
            self.meta["ignored_depth"] = 100
            numbered = True

        if numbered:
            title, number_list = split_number(title)
            if number_list:
                self.number_list[kind] = [0] * 6
                self.number_list[kind][depth : depth + len(number_list)] = number_list
            else:
                self.number_list[kind][depth] += 1
                reset = [0] * (5 - depth)
                self.number_list[kind][depth + 1 :] = reset
            number_list = normalize_number_list(self.number_list, kind, depth)
            number_string = number_list_format(number_list)
        else:
            number_list = []
            number_string = ""

        header = context["prefix"] if kind == "header" else ""
        prefix = self.config["kind_prefix"][kind] if kind != "header" else ""
        title, tag = split_tag(title)
        title, inline_pattern = split_inline_pattern(title)
        context = {
            "kind": kind,
            "header": header,
            "prefix": prefix,
            "title": title,
            "_title": context["title"],
            "number_list": number_list,
            "number_string": number_string,
            "inline_pattern": inline_pattern,
        }

        if tag:
            self.tag_context[tag] = {
                "kind": kind,
                "number_list": number_list,
                "number_string": number_string,
                "abs_src_path": self.abs_src_path,
            }
            context.update(tag=tag)
        return context


def get_content_from_cell(cell, kind, splitter, parser) -> str:
    if cell.source.startswith("~~~") and kind in "figure table":
        content = cell.context["source"] + "\n"
        content = parser.parse(content, decorate=False)
        return Header.markdown.convert(content)
    else:
        if cell.source.startswith("```") and kind in "figure table":
            cell.context["option"] += " inline"
        return parser.parse_from_cell(cell, splitter)


def get_content(source: str) -> Tuple[str, str]:
    source = source.lstrip()
    if source == "":
        return "", ""
    index = source.find("\n\n")
    if index == -1:
        content, rest = source, ""
    else:
        content, rest = source[:index], "\n" + source[index + 2 :]
    content = Header.markdown.convert(content)
    return content, rest


class Anchor(Renderer):
    header: Optional[Header] = field(default=None)
    abs_src_path: str = field(default=".")  # should be set the real path later

    def init(self):
        self.register(Header.TAG_PATTERN, self.render_tag)
        self.set_template("anchor")

    @comment("tag")
    def render_tag(self, context, splitter, parser) -> Iterator[str]:
        tag = context["tag"]
        context = self.resolve(tag)
        yield self.render("anchor", context, reference=True)

    def resolve(self, tag: str) -> Dict[str, Any]:
        if self.header is None:
            raise ValueError("A Header instance has not set yet.")
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
        return number_list["header"][:depth] + [
            num for num in number_list[kind][depth:] if num
        ]


def number_list_format(number_list: List[int]) -> str:
    return ".".join([str(x) for x in number_list if x])


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


def split_inline_pattern(title: str) -> Tuple[str, str]:
    """Split an inline pattern from `title`. Return (title, inline pattern).

    Parameters
    ----------
    title
        header text

    Returns
    -------
    (title, inline pattern)
    """
    match = re.search(r"\{.+\}", title)
    if match:
        inline_pattern = match.group()
        title = title.replace(inline_pattern, "").strip()
        return title, inline_pattern
    else:
        return title, ""


def split_number(title: str) -> Tuple[str, List[int]]:
    if title and "1" <= title[0] <= "9":
        index = title.find(" ")
        if index != -1:
            number, title = title[:index], title[index + 1 :]
        else:
            number, title = title, ""
        number_list = [int(num) for num in number.split(".")]
    else:
        number_list = []
    return title, number_list

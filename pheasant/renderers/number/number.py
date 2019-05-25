"""Automatic numbering renderer."""
import os
import re
from dataclasses import field
from typing import Any, Dict, Iterator, List, Optional, Tuple

from markdown import Markdown

from pheasant.core.decorator import commentable
from pheasant.core.renderer import Renderer


class Header(Renderer):
    tag_context: Dict[str, Any] = field(default_factory=dict)
    number_list: Dict[str, List[int]] = field(default_factory=dict)
    header_kind: Dict[str, str] = field(default_factory=dict)

    HEADER_PATTERN = r"^(?P<prefix>#+)(?P<header>[!\w]*) *(?P<title>.*?)\n"
    TAG_PATTERN = r"\{#(?P<tag>.+?)#\}"
    # TAG_PATTERN = r"\{#(?P<tag>\S+?)#\}"

    markdown = Markdown(extensions=["tables"])

    def init(self):
        self.register(Header.HEADER_PATTERN, self.render_header)
        self.set_template("header")
        self.header_kind.update(fig="figure", tab="table", eq="equation")
        prefix = dict(figure="Figure", table="Table")
        self.set_config(prefix=prefix, number=dict(separator="."))
        self.start()

    def start(self) -> None:
        self.meta["ignored_path"] = set()
        self.meta["ignored_depth"] = 100
        for kind in list(self.config["prefix"].keys()) + ["header", "equation"]:
            self.number_list[kind] = [0] * 6

    def render_header(self, context, splitter, parser) -> Iterator[str]:
        if context["header"] == "!":
            self.start()
            return
        context = self.resolve(context)
        kind = context["kind"]
        if kind == "header":
            if context["inline_pattern"]:
                context["title"] = parser.parse(context["_title"], decorate=False)
            yield self.render("header", context) + "\n\n"
        elif kind == "equation":
            content = split_tag(context["_title"])[0]
            context["environment"] = kind
            if content.startswith("* "):
                content = content[2:]
                context["environment"] += "*"
            context["content"] = parser.parse(content, decorate=False)
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
        header = context["header"][:3].lower()
        if header and header not in self.header_kind:
            kind = context["header"]
            if kind not in self.config["prefix"]:
                self.number_list[kind] = [0] * 6
                self.config["prefix"][kind] = kind
        else:
            kind = self.header_kind.get(header, "header")

        depth = len(context["prefix"]) - 1
        title = context["title"]

        numbered = False
        if title.startswith("##"):
            title = title[2:]
            self.meta["ignored_path"].add(self.page.path)
        elif title.startswith("#"):
            title = title[1:]
            self.meta["ignored_depth"] = depth
        elif self.page.path in self.meta["ignored_path"]:
            pass
        elif depth > self.meta["ignored_depth"]:
            pass
        else:
            self.meta["ignored_depth"] = 100
            numbered = True

        if title.startswith("!"):
            title = title[1:]
            self.number_list[kind] = [0] * 6

        if numbered:
            title, number_list = split_number(title)
            if number_list:
                self.number_list[kind] = [0] * 6
                self.number_list[kind][depth : depth + len(number_list)] = number_list
                if kind == "header":
                    depth += len(number_list) - 1
                    context["prefix"] = "#" * (depth + 1)
            else:
                self.number_list[kind][depth] += 1
                reset = [0] * (5 - depth)
                self.number_list[kind][depth + 1 :] = reset
            number_list = normalize_number_list(self.number_list, kind, depth)
            func = self.config["number"].get
            args = [func(key, "") for key in ["separator", "prefix", "suffix"]]
            number_string = number_list_format(number_list, *args)
        else:
            number_list = []
            number_string = ""

        header = context["prefix"] if kind == "header" else ""
        prefix = self.config["prefix"].get(kind, "")
        title, tag = split_tag(title)
        title, inline_pattern = split_inline_pattern(title)
        title, link = split_link(title)
        context = {
            "kind": kind,
            "header": header,
            "prefix": prefix,
            "title": title,
            "_title": context["title"],
            "number_list": number_list,
            "number_string": number_string,
            "inline_pattern": inline_pattern,
            "link": link,
        }

        if tag:
            self.tag_context[tag] = {
                "kind": kind,
                "number_list": number_list,
                "number_string": number_string,
                "path": self.page.path,
                "title": title,
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

    def init(self):
        self.register(Header.TAG_PATTERN, self.render_tag)
        self.set_template("anchor")

    @commentable("tag")
    def render_tag(self, context, splitter, parser) -> Iterator[str]:
        tag = context["tag"]
        context = self.resolve(tag)
        yield self.render("anchor", context, reference=True)

    def resolve(self, tag: str) -> Dict[str, Any]:
        if self.header is None:
            raise ValueError("A Header instance has not set yet.")
        if "|" in tag:
            tag, fmt = tag.split("|")
            fmt = fmt.strip()
        else:
            fmt = ""
        tag = tag.strip()
        tag_context = self.header.tag_context  # type: ignore
        found = tag in tag_context
        context = {"found": found, "tag": tag}
        if found:
            context.update(tag_context[tag])
            if fmt:
                context["number_string"] = format_tag(
                    fmt, context["number_list"], context["title"]
                )
            try:
                relpath = os.path.relpath(  # type: ignore
                    context["path"], os.path.dirname(self.page.path)
                )
            except ValueError:
                relpath = ""
            relpath = relpath.replace("\\", "/")
            context["ref"] = "#".join([relpath, tag])
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


def number_list_format(
    number_list: List[int], sep: str = ".", prefix: str = "", suffix: str = ""
) -> str:
    return "".join([prefix, sep.join([str(x) for x in number_list]), suffix])


RE_TAG_PATTERN = re.compile(Header.TAG_PATTERN)


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
    match = RE_TAG_PATTERN.search(title)
    if match:
        return title.replace(match.group(), "").strip(), match.group(1).strip()
    else:
        return title, ""


RE_INLINE_PATTERN = re.compile(r"\{.+\}")


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
    match = RE_INLINE_PATTERN.search(title)
    if match:
        inline_pattern = match.group()
        title = title.replace(inline_pattern, "").strip()
        return title, inline_pattern
    else:
        return title, ""


RE_NUMBER_PATTERN = re.compile(r"[0-9]+\.")


def split_number(title: str) -> Tuple[str, List[int]]:
    if RE_NUMBER_PATTERN.match(title):
        index = title.find(" ")
        if index != -1:
            number, title = title[:index], title[index + 1 :]
            if number.endswith("."):
                number = number[:-1]
        else:
            number, title = title, ""
        number_list = [int(num) for num in number.split(".")]
    else:
        number_list = []
    return title, number_list


RE_LINK_PATTERN = re.compile(r"\(https?://.*?\)")


def split_link(title: str) -> Tuple[str, str]:
    """Split a link from `title`. Return (title, link)."""
    match = RE_LINK_PATTERN.search(title)
    if match:
        link = match.group()
        title = title.replace(link, "").strip()
        return title, link[1:-1].replace("/ ", "/")
    else:
        return title, ""


def format_tag(fmt: str, number_list, title) -> str:
    for k in range(len(number_list)):
        fmt = fmt.replace(str(k + 1), str(number_list[k]))
    fmt = fmt.replace('title', title)
    return fmt

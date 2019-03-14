import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from pheasant.core import markdown
from pheasant.core.parser import Parser
from pheasant.core.renderer import Config, Context, Renderer


class Number(Renderer):

    HEADER_PATTERN = r"^(?P<prefix>#+)(?P<kind>\S*?) +(?P<title>.+?)\n"
    LABEL_PATTERN = r"\{#(?P<label>\S+?)#\}"

    def __init__(
        self, parser: Optional[Parser] = None, config: Optional[Config] = None
    ):
        super().__init__(parser, config)
        self.parser.register(Number.HEADER_PATTERN, self.render_header)
        self.parser.register(Number.LABEL_PATTERN, self.render_label)
        self.set_template("header")
        self.page_index: Union[int, List[int]] = 1
        self.label_context: Dict[str, Any] = {}
        self.number_list: Dict[str, List[int]] = {}
        self.header_kind: Dict[str, str] = {}
        self.abs_src_path = "."
        for kind in self.config["kind"]:
            if kind == "header":
                self.header_kind[""] = "header"
            else:
                self.header_kind[kind[:3].lower()] = kind
                default_prefix = kind[0].upper() + kind[1:]
                self.config["kind_prefix"].setdefault(kind, default_prefix)
        self.reset_number_list()

    def reset_number_list(self) -> None:
        for kind in self.config["kind"]:
            self.number_list[kind] = [0] * 6

    def save_label_context(self):
        for key in self.label_context:
            self.label_context[key].update(abs_src_path=self.abs_src_path)

        label_file = self.config["label_file"]
        if os.path.exists(label_file):
            with open(label_file, "r") as file:
                label_context_all = json.load(file)
                label_context_all.update(self.label_context)
        else:
            label_context_all = self.label_context

        if os.path.exists(label_file):
            os.remove(label_file)
        with open(label_file, "w") as file:
            json.dump(label_context_all, file)

        for key in label_context_all:
            label_context = label_context_all[key]
            relpath = os.path.relpath(
                label_context["abs_src_path"], os.path.dirname(self.abs_src_path)
            )
            relpath = relpath.replace("\\", "/")
            if self.config["relpath_function"]:
                relpath = self.config["relpath_function"](relpath)
            label_context["ref"] = "#".join([relpath, label_context["id"]])

        self.label_context = label_context_all

    def render_header(self, context: Context, parser: Parser) -> Iterable[str]:
        kind = self.header_kind[context["kind"][:3].lower()]
        depth = len(context["prefix"]) - 1
        self.number_list[kind][depth] += 1
        reset = [0] * (len(self.number_list[kind]) - depth)
        self.number_list[kind][depth + 1 :] = reset
        number_list = self.number_list[kind][: depth + 1]
        if kind == "header":
            prefix = "#" * len(number_list)
        else:
            prefix = self.config["kind_prefix"][kind]
        number_list = normalize_number_list(kind, number_list, self.page_index)
        cls = self.config["class"].format(kind=kind)
        title, label = split_label(context["title"])

        context_ = {
            "prefix": prefix,
            "title": title,
            "class": cls,
            "kind": kind,
            "number_list": number_list,
        }

        if label:
            id_ = self.config["id"].format(label=label)
            self.label_context[label] = {
                "kind": kind,
                "number_list": number_list,
                "id": id_,
                "abs_src_path": self.abs_src_path,
            }
            context_.update(label=label, id=id_)

        if kind == "header":
            yield self.config["header_template"].render(**context_, config=self.config)
        else:
            # Need to detect the range of a numbered object.
            content = parser.send(all)
            if content["match"]:
                content = content["result"]()
                rest = ""
            else:
                content = content["source"]
                if content.startswith(self.config["begin_pattern"]):
                    content = content[len(self.config["begin_pattern"]) :]
                    content, *rests = content.split(self.config["end_pattern"])
                    rest = self.config["end_pattern"].join(rests)
                else:
                    index = content.find("\n\n")
                    if index == -1:
                        content, rest = content, ""
                    else:
                        content, rest = content[:index], content[index + 2 :]

                content = markdown.convert(content)

            yield self.config["header_template"].render(
                **context_, content=content, config=self.config
            )

            if rest:
                yield rest

    def render_label(self, context: Context, parser: Parser) -> Iterable[str]:
        label = context["label"]
        found = label in self.label_context
        context = self.label_context[label] if found else {"label": label}
        yield self.config["header_template"].render(
            reference=True, found=found, config=self.config, **context
        )


def normalize_number_list(
    kind: str, number_list: List[int], page_index: Union[int, List[int]]
) -> List[int]:
    """

    Examples
    --------
    >>> normalize_number_list("header", [1], 1)
    [1]
    >>> normalize_number_list("header", [1, 2], [3])
    [3, 2]
    >>> normalize_number_list("header", [0, 2], 2)
    [2]
    >>> normalize_number_list("header", [0, 2], 1)
    [0, 2]
    >>> normalize_number_list("header", [0, 2, 1], 2)
    [2, 1]
    >>> normalize_number_list("figure", [3], 1)
    [3]
    >>> normalize_number_list("figure", [3], [4, 2])
    [4, 2, 3]
    >>> normalize_number_list("figure", [3, 1], 2)
    [3, 1]
    """
    if isinstance(page_index, list):
        if kind == "header":
            number_list = page_index + number_list[1:]
        else:
            number_list = page_index + number_list
    else:
        if kind == "header":
            number_list = number_list[page_index - 1 :]

    return number_list


def split_label(title: str) -> Tuple[str, str]:
    """Split a label from `title`. Return (title, label).

    Parameters
    ----------
    title
        header text

    Returns
    -------
    (title, label)

    Examples
    --------
    >>> split_label('{#label#} text')
    ('text', 'label')
    >>> split_label('text')
    ('text', '')
    """
    match = re.search(Number.LABEL_PATTERN, title)
    if match:
        return title.replace(match.group(), "").strip(), match.group(1)
    else:
        return title, ""

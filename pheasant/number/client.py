import logging
import os
import re
from typing import Any, Dict, List, Optional, Union, Iterable, Tuple

from jinja2 import Environment, FileSystemLoader

from pheasant.core.converter import Client
from pheasant.markdown.converter import markdown_convert
logger = logging.getLogger("mkdocs")

HEADER_PATTERN = r"^(?P<sharp>#+)(?P<kind>\S*?)\s+(?P<title>[^\n.]+?)$"
LABEL_PATTERN = r"\{#(?P<label>\S+?)#\}"


class Number(Client):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("number", config)
        self.abs_src_path: Optional[str] = None
        self.register("header", HEADER_PATTERN, self.header)
        self.register("reference", LABEL_PATTERN, self.reference)
        self.set_template()
        self.label: Dict[str, Any] = {}
        self.page_index: Union[int, List[Any]] = []
        self.number_list: Dict[str, List[int]] = {}
        self.header_kind: Dict[str, str] = {}
        for kind in self.config["kind"]:
            if kind == "header":
                self.header_kind[""] = "header"
            else:
                self.header_kind[kind[:3].lower()] = kind

    def register_pages(self, abs_src_paths: List[str]) -> None:
        """Register pages before conversion due to maintain the order of pages.

        Parameters
        ----------
        abs_src_paths
            List of pages. Absolute file paths.
        """
        self.config["pages"] = list(abs_src_paths)

        for path in abs_src_paths:
            if (
                re.match(self.config["ignore_pattern"], path)
                and path not in self.config["ignore_pages"]
            ):
                self.config["ignore_pages"].append(path)
                del self.config["pages"][self.config["pages"].index(path)]
        logger.info(
            f'[Pheasant.number] {len(self.config["pages"])} pages are registered.'
        )
        logger.info(
            f'[Pheasant.number] {len(self.config["ignore_pages"])} pages are ignored.'
        )

    def set_template(self):
        default_directory = os.path.join(os.path.dirname(__file__), "templates")

        abspath = os.path.abspath(self.config["template_file"])
        template_directory, template_file = os.path.split(abspath)
        env = Environment(
            loader=FileSystemLoader([template_directory, default_directory]),
            autoescape=False,
        )
        self.config["template"] = env.get_template(template_file)

    def on_page_read_source(self, abs_src_path: str) -> None:
        self.abs_src_path = abs_src_path
        if abs_src_path in self.config["ignore_pages"]:
            self.enable = False
            return
        else:
            self.enable = True
        if abs_src_path not in self.config["pages"]:
            self.config["pages"].append(abs_src_path)
        if self.config["level"] == 0:
            self.page_index = [self.config["pages"].index(abs_src_path) + 1]
        else:
            self.page_index = self.config["level"]
        self.number_list = {}
        for kind in self.config["kind"]:
            self.number_list[kind] = [0] * 6

    def reference(self, context: Dict[str, str]) -> Iterable[str]:
        yield "xyz"
        pass

    def header(self, context: Dict[str, str]) -> Iterable[str]:
        print('!!!!!!!!!!!!!!!!!!!!')
        print(context)
        print('!!!!!!!!!!!!!!!!!!!!')
        kind = context["kind"]
        kind = self.header_kind[kind[:3].lower()]
        context["kind"] = kind
        depth = len(context["sharp"]) - 1
        self.number_list[kind][depth] += 1
        reset = [0] * (len(self.number_list[kind]) - depth)
        self.number_list[kind][depth + 1 :] = reset
        number_list = self.number_list[kind][: depth + 1]

        if kind == "header":
            prefix = "#" * len(number_list)
        else:
            default_prefix = kind[0].upper() + kind[1:]
            prefix = self.config["kind_prefix"].get(kind, default_prefix)
        number_list = normalize_number_list(kind, number_list, self.page_index)

        cls = self.config["class"].format(kind=kind)

        extra_context = {
            "prefix": prefix,
            "number_list": number_list,
            "class": cls,
        }

        title, label = split_label(context["title"])

        if label:
            id_ = self.config["id"].format(label=label)
            self.label[label] = {"kind": kind, "number_list": number_list, "id": id_}
            extra_context["id"] = id_
            extra_context["label"] = label

        if kind == "header":
            print(context)
            print(extra_context)
            yield self.config["template"].render(
                **context, **extra_context, config=self.config
            )
        else:
            # Detect the range of numbered object.
            print(context)
            print(extra_context)
            print(self.renderer.generator)
            next_source = next(self.renderer.generator)
            if not isinstance(next_source, str):
                raise ValueError("Invalid source")
            elif next_source.startswith(self.config["begin_pattern"]):
                next_source = next_source[len(self.config["begin_pattern"]) :]
                content, *rests = next_source.split(self.config["end_pattern"])
                rest = self.config["end_pattern"].join(rests)
            else:
                index = next_source.find("\n\n")
                if index == -1:
                    content, rest = next_source, ""
                else:
                    content = next_source[:index]
                    rest = next_source[index + 2 :]
            extensions = ["tables"] + self.config["markdown_extensions"]
            content = markdown_convert(content, extensions=extensions)

            if "title" in context:  # for Math in title
                title = markdown_convert(context["title"], extensions=extensions)
                if title.startswith("<p>") and title.endswith("</p>"):
                    title = title[3:-4]
                context["title"] = title
            yield self.config["template"].render(
                **context, **extra_context, content=content, config=self.config
            )

            if rest:
                yield rest


def normalize_number_list(
    kind: str, number_list: list, page_index: Union[int, list]
) -> list:
    if isinstance(page_index, list):
        if kind == "header":
            number_list = page_index + number_list[1:]
        else:
            number_list = page_index + number_list
    else:
        if kind == "header":
            number_list = number_list[page_index - 1 :]
    return number_list


LABEL_PATTERN_COMPILED = re.compile(LABEL_PATTERN)


def split_label(text: str) -> Tuple[str, str]:
    """
    Split a label from `text`. Label

    Parameters
    ----------
    text : str
        header text

    Examples
    --------
    >>> split_label('{#label#} text')
    ('text', 'label')
    >>> split_label('text')
    ('text', '')
    """
    m = re.search(LABEL_PATTERN_COMPILED, text)
    if not m:
        return text, ""
    else:
        return text.replace(m.group(), "").strip(), m.group(1)


# def convert(source: str) -> str:
#
#     source, label = convert_header(source, label, page_index)
#     for key in label:
#         label[key].update(path=source_file)
#     if os.path.exists(config["label_file"]):
#         with open(config["label_file"], "r") as file:
#             label_all = json.load(file)
#     else:
#         label_all = {}
#     label_all.update(label)
#
#     if os.path.exists(config["label_file"]):
#         os.remove(config["label_file"])
#     with open(config["label_file"], "w") as file:
#         json.dump(label_all, file)
#     for key in label_all:
#         id = label_all[key]
#         relpath = os.path.relpath(
#             id["path"] or "<dummy>",  # dummy for pytest
#             os.path.dirname(source_file or "dummy"),
#         )
#         relpath = relpath.replace("\\", "/")
#         if config["relpath_function"]:
#             relpath = config["relpath_function"](relpath)
#         else:
#             relpath = relpath.replace(".ipynb", "")  # for MkDocs
#         id["ref"] = "#".join([relpath, label_all[key]["id"]])
#     source = convert_reference(source, label_all)
#
#     return source
#

import json
import logging
import os
import re
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader

from pheasant.number.config import config
from pheasant.number.header import convert as convert_header
from pheasant.number.reference import convert as convert_reference

logger = logging.getLogger("mkdocs")


def register_pages(source_files: List[str]) -> None:
    """Register pages before conversion due to maintain the order of pages.

    Parameters
    ----------
    source_files
        List of pages. Absolute file paths.
    """
    config["pages"] = source_files


def initialize() -> None:
    for path in list(config["pages"]):  # `list` is needed for iteration.
        if (
            re.match(config["ignore_pattern"], path)
            and path not in config["ignore_pages"]
        ):
            config["ignore_pages"].append(path)
            del config["pages"][config["pages"].index(path)]

    logger.info(f'[Pheasant.number] {len(config["pages"])} pages are ' "registered.")
    logger.info(
        f'[Pheasant.number] {len(config["ignore_pages"])} pages are ' "ignored."
    )

    default_directory = os.path.join(os.path.dirname(__file__), "templates")

    abspath = os.path.abspath(config["template_file"])
    template_directory, template_file = os.path.split(abspath)
    env = Environment(
        loader=FileSystemLoader([template_directory, default_directory]),
        autoescape=False,
    )
    config["template"] = env.get_template(template_file)

    config["LABEL_PATTERN"] = re.compile(config["label_pattern"])


def convert(source: str) -> str:
    from pheasant.converters import get_source_file

    source_file = get_source_file()

    if source_file in config["ignore_pages"]:
        return source
    elif source_file not in config["pages"]:
        config["pages"].append(source_file)

    if config["level"] == 0:
        page_index = [config["pages"].index(source_file) + 1]
    else:
        page_index = config["level"]

    label: Dict[str, Any] = {}
    source, label = convert_header(source, label, page_index)
    for key in label:
        label[key].update(path=source_file)

    if os.path.exists(config["label_file"]):
        with open(config["label_file"], "r") as file:
            label_all = json.load(file)
    else:
        label_all = {}

    label_all.update(label)

    if os.path.exists(config["label_file"]):
        os.remove(config["label_file"])
    with open(config["label_file"], "w") as file:
        json.dump(label_all, file)

    for key in label_all:
        id = label_all[key]
        relpath = os.path.relpath(
            id["path"] or "<dummy>",  # dummy for pytest
            os.path.dirname(source_file or "dummy"),
        )
        relpath = relpath.replace("\\", "/")
        if config["relpath_function"]:
            relpath = config["relpath_function"](relpath)
        else:
            relpath = relpath.replace(".ipynb", "")  # for MkDocs
        id["ref"] = "#".join([relpath, label_all[key]["id"]])

    source = convert_reference(source, label_all)

    return source

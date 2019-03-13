import re
from typing import Any, Dict, Iterator, Tuple, Union

from pheasant.number.client import LABEL_PATTERN


def render(
    context: Dict[str, str], label: Dict[str, Any], page_index: Union[int, list],
    number_list:Dict[str,List[int]], header_kind:Dict[str,str]
) -> Iterator[str]:
    kind = context["kind"]
    depth = len(context["sharp"]) - 1
    number_list[kind][depth] += 1
    reset = [0] * (len(number_list[kind]) - depth)
    number_list[kind][depth + 1 :] = reset
    title, label = split_label(splitted.group(3))
    number_list = number_list[kind][:depth+1]



    if kind == "header":
        context["prefix"] = "#" * len(number_list)
    else:
        default_prefix = kind[0].upper() + kind[1:]
        prefix = config["kind_prefix"].get(kind, default_prefix)
        context["prefix"] = prefix

    number_list = normalize_number_list(kind, context["number_list"], page_index)
    context["number_list"] = number_list

    cls = config["class"].format(kind=kind)
    context["class"] = cls

    if context["label"]:
        context["id"] = config["id"].format(label=context["label"])
        label[context["label"]] = {
            "kind": kind,
            "number_list": context["number_list"],
            "id": context["id"],
        }

    if kind == "header":
        yield config["template"].render(**context, config=config)
    else:
        # Detect the range of numbered object.
        next_source = next(splitter)
        if not isinstance(next_source, str):
            raise ValueError("Invalid source")
        elif next_source.startswith(config["begin_pattern"]):
            next_source = next_source[len(config["begin_pattern"]) :]
            content, *rests = next_source.split(config["end_pattern"])
            rest = config["end_pattern"].join(rests)
        else:
            index = next_source.find("\n\n")
            if index == -1:
                content, rest = next_source, ""
            else:
                content = next_source[:index]
                rest = next_source[index + 2 :]

        extensions = ["tables"] + config["markdown_extensions"]
        content = markdown_convert(content, extensions=extensions)

        if "title" in context:  # for Math in title
            title = markdown_convert(context["title"], extensions=extensions)
            if title.startswith("<p>") and title.endswith("</p>"):
                title = title[3:-4]
            context["title"] = title

        yield config["template"].render(**context, content=content, config=config)

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
    m = re.search(config["label_pattern"], text)
    if not m:
        return text, ""
    else:
        return text.replace(m.group(), "").strip(), m.group(1)

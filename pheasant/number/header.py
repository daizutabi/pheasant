import re
from typing import Generator, Tuple, Union

from pheasant.markdown.converter import markdown_convert
from pheasant.markdown.splitter import escaped_splitter_join

from .config import config


def convert(source: str, label=None,
            page_index: Union[int, list] = 1) -> Tuple[str, dict]:
    """
    Convert markdown string or file into markdown with section number_listing.

    Parameters
    ----------
    source : str
        Markdown source string.
    page_index : list of in or int
        Page index.
        If list, page index from parents
        If int, it is a start level of numbering. For example, 2 for h2.

    Returns
    -------
    tuple
        Markdown source
    """
    label = {} if label is None else label
    source = '\n\n'.join(renderer(source, label, page_index=page_index))
    return source, label


def renderer(source: str, label: dict,
             page_index: Union[int, list] = 1) -> Generator[str, None, None]:
    splitter = header_splitter(source)
    for splitted in splitter:
        if isinstance(splitted, str):
            yield splitted
            continue

        kind = splitted['kind']
        if kind == 'header':
            splitted['prefix'] = '#' * len(splitted['number_list'])
        else:
            default_prefix = kind[0].upper() + kind[1:] + ' '
            prefix = config['kind_prefix'].get(kind, default_prefix)
            splitted['prefix'] = prefix

        number_list = normalize_number_list(kind, splitted['number_list'],
                                            page_index)
        splitted['number_list'] = number_list

        cls = config['class'].format(kind=kind)
        splitted['class'] = cls

        if splitted['label']:
            splitted['id'] = config['id'].format(label=splitted['label'])
            label[splitted['label']] = {
                'kind': kind,
                'number_list': splitted['number_list'],
                'id': splitted['id']
            }

        if kind == 'header':
            yield config['template'].render(**splitted, config=config)
        else:
            # Detect the range of numbered object.
            next_source = next(splitter)
            if not isinstance(next_source, str):
                raise ValueError('Invalid source')
            elif next_source.startswith(config['begin_pattern']):
                next_source = next_source[len(config['begin_pattern']):]
                content, *rests = next_source.split(config['end_pattern'])
                rest = config['end_pattern'].join(rests)
            else:
                index = next_source.find('\n\n')
                if index == -1:
                    content, rest = next_source, ''
                else:
                    content = next_source[:index]
                    rest = next_source[index + 2:]

            extensions = ['tables'] + config['markdown_extensions']
            content = markdown_convert(content, extensions=extensions)

            if 'title' in splitted:  # for Math in title
                title = markdown_convert(
                    splitted['title'], extensions=extensions)
                if title.startswith('<p>') and title.endswith('</p>'):
                    title = title[3:-4]
                splitted['title'] = title

            yield config['template'].render(
                **splitted, content=content, config=config)

            if rest:
                yield rest


def header_splitter(source: str) -> Generator[Union[str, dict], None, None]:
    """
    Generate splitted markdown header and body text from `source`.

    # normal header.

    #Figure, #FIG., etc for figure
    #Table, #tab, etc for table
    #Code, #code, etc for code

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    splitted source : str or dict
    """
    number_list = {}
    header_kind = {}
    for kind in config['kind']:
        number_list[kind] = [0] * 6
        if kind == 'header':
            header_kind[''] = 'header'
        else:
            header_kind[kind[:3].lower()] = kind
    cursor = 0

    pattern_escape = r'(```(.*?)```)|(~~~(.*?)~~~)'
    pattern_header = r'^(#+)(\S*?) (.+?)$'

    splitter = escaped_splitter_join(pattern_header, pattern_escape, source)
    for splitted in splitter:
        if isinstance(splitted, str):
            splitted = splitted.strip()
            if splitted:
                yield splitted
        else:
            start, end = splitted.span()
            cursor += start
            kind = header_kind[splitted.group(2)[:3].lower()]
            depth = len(splitted.group(1)) - 1
            number_list[kind][depth] += 1
            reset = [0] * (len(number_list[kind]) - depth)
            number_list[kind][depth + 1:] = reset
            title, label = split_label(splitted.group(3))

            context = {
                'kind': kind,
                'title': title,
                'label': label,
                'cursor': cursor,
                'number_list': number_list[kind][:depth + 1]
            }
            cursor += end

            yield context


def normalize_number_list(kind, number_list, page_index=None):
    if isinstance(page_index, list):
        if kind == 'header':
            number_list = page_index + number_list[1:]
        else:
            number_list = page_index + number_list
    else:
        if kind == 'header':
            number_list = number_list[page_index - 1:]

    return number_list


def split_label(text):
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
    m = re.search(config['label_pattern'], text)
    if not m:
        return text, ''
    else:
        return text.replace(m.group(), '').strip(), m.group(1)

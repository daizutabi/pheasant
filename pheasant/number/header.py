import re
import nbformat

from ..utils import escaped_splitter_join, read_source
from .config import config
from ..jupyter.exporter import run_and_export
from ..markdown.convert import markdown_convert


def convert(source: str, label=None, page_index=1):
    """
    Convert markdown string or file into markdown with section number_listing.

    Parameters
    ----------
    source : str
        Markdown source string or filekind
    page_index : list of in or int
        Page index.
        If list, page index from parents
        If int, it is a start level of numbering. For example, 2 for h2.

    Returns
    -------
    results : str
        Markdown source
    """
    label = {} if label is None else label
    source = read_source(source)
    source = '\n\n'.join(renderer(source, label, page_index=page_index))
    return source, label


def renderer(source: str, label: dict, page_index=1):
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
            if next_source.startswith('#begin\n'):
                content, rest = next_source[7:].split('#end')
            else:
                index = next_source.find('\n\n')
                if index == -1:
                    content, rest = next_source, ''
                else:
                    content = next_source[:index]
                    rest = next_source[index + 2:]

            extensions = config['markdown_extensions']
            content = markdown_convert(content, extensions=extensions)

            if 'title' in splitted:  # for Math in title
                # title = md.convert(splitted['title'])
                title = markdown_convert(splitted['title'],
                                         extensions=extensions)
                if title.startswith('<p>') and title.endswith('</p>'):
                    title = title[3:-4]
                splitted['title'] = title

            yield config['template'].render(
                **splitted, content=content, config=config)

            if rest:
                yield rest


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


def header_splitter(source: str):
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

    for splitted in escaped_splitter_join(pattern_header, pattern_escape,
                                          source):
        if isinstance(splitted, str):
            yield splitted.strip()
        else:
            start, end = splitted.span()
            cursor += start
            kind = header_kind[splitted.group(2)[:3].lower()]
            depth = len(splitted.group(1)) - 1
            number_list[kind][depth] += 1
            reset = [0] * (len(number_list[kind]) - depth)
            number_list[kind][depth + 1:] = reset
            title, label = split_label(splitted.group(3))
            yield {
                'kind': kind,
                'title': title,
                'label': label,
                'cursor': cursor,
                'number_list': number_list[kind][:depth + 1]
            }
            cursor += end

            if kind == 'code':
                yield inspect_source(title)


def inspect_source(source: str) -> str:
    """Inspect source code."""
    name, *options = source.split(' ')
    name, *line_range = name.split(':')

    cell = nbformat.v4.new_code_cell(f'inspect.getsourcelines({name})')
    markdown = run_and_export(cell, inspect_export)

    return f'#begin\n``` python\n{markdown}```\n#end'


def inspect_export(cell) -> str:
    """Convert a cell generated by inspection into markdown."""
    for output in cell['outputs']:
        if 'data' in output and 'text/plain' in output['data']:
            lines, lineno = eval(output['data']['text/plain'])
            return ''.join(lines)
            break
    else:
        return ''

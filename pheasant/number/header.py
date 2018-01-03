import re

from markdown import Markdown

from ..utils import escaped_splitter, read_source
from .config import config


def convert(source: str, tag=None, page_index=None):
    """
    Convert markdown string or file into markdown with section number_listing.

    Parameters
    ----------
    source : str
        Markdown source string or filekind
    page_index : list of int
        Page index.

    Returns
    -------
    results : str
        Markdown source
    """
    tag = {} if tag is None else tag
    source = read_source(source)
    source = '\n\n'.join(renderer(source, tag, page_index=page_index))
    return source, tag


def renderer(source: str, tag: dict, page_index=None):
    splitter = header_splitter(source)
    for splitted in splitter:
        if isinstance(splitted, str):
            yield splitted
        else:
            if splitted['kind'] == 'header':
                splitted['prefix'] = '#' * len(splitted['number_list'])
            number_list = normalize_number_list(splitted['kind'],
                                                splitted['number_list'],
                                                page_index)
            splitted['number_list'] = number_list
            cls = config['class'].format(kind=splitted['kind'])
            splitted['class'] = cls
            if splitted['tag']:
                splitted['id'] = config['id'].format(tag=splitted['tag'])
                tag[splitted['tag']] = {'kind': splitted['kind'],
                                        'number_list': splitted['number_list'],
                                        'id': splitted['id']}

            if splitted['kind'] == 'header':
                yield config['template'].render(**splitted, config=config)
            else:
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

                md = Markdown(extensions=['markdown.extensions.tables',
                                          'markdown.extensions.fenced_code'])
                content = md.convert(content)

                yield config['template'].render(**splitted, content=content,
                                                config=config)

                if rest:
                    yield rest


def normalize_number_list(kind, number_list, page_index=None):
    if page_index:
        if kind == 'header':
            number_list = page_index + number_list[1:]
        else:
            number_list = page_index + number_list
    return number_list


def split_tag(text):
    """
    Split a tag from `text`. Tag is

    Parameters
    ----------
    text : str
        header text

    Examples
    --------
    >>> split_tag('{#tag#} text')
    ('text', 'tag')
    >>> split_tag('text')
    ('text', '')
    """
    m = re.search(config['tag_pattern'], text)
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

    pattern_escape = r'(^```(.*?)^```$)|(^~~~(.*?)^~~~$)'
    pattern_header = r'^(#+)(\S*?) (.+?)$'

    for splitted in escaped_splitter(pattern_header, pattern_escape, source):
        if isinstance(splitted, str):
            markdown = splitted.strip()
            if markdown:
                yield markdown
        else:
            start, end = splitted.span()
            cursor += start
            kind = header_kind[splitted.group(2)[:3].lower()]
            depth = len(splitted.group(1)) - 1
            number_list[kind][depth] += 1
            reset = [0] * (len(number_list[kind]) - depth)
            number_list[kind][depth + 1:] = reset
            title, tag = split_tag(splitted.group(3))
            yield {'kind': kind, 'title': title, 'tag': tag, 'cursor': cursor,
                   'number_list': number_list[kind][:depth + 1]}
            cursor += end

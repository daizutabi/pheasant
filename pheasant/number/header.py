import re

from jinja2 import Environment, PackageLoader, Template, select_autoescape

from markdown import Markdown

from ..utils import read_source
from .config import config


def convert(source: str, page_index=None):
    """
    Convert markdown string or file into markdown with section numbering.

    Parameters
    ----------
    source : str
        Markdown source string or filename
    page_index : list of int
        Page index.

    Returns
    -------
    results : str
        Markdown source
    """
    tag_dictionary = {}
    source = read_source(source)
    source = '\n\n'.join(renderer(source, tag_dictionary,
                                  page_index=page_index))
    return source, tag_dictionary


def renderer(source: str, tag_dictionary, page_index=None):
    # env = Environment(
    #     loader=PackageLoader('pheasant.number', 'templates'),
    #     autoescape=select_autoescape(['html', 'xml', 'jinja2'])
    # )
    # template = env.get_template(config['template_file'])

    template = Template(read_source(config['template_file']))

    splitter = header_splitter(source)
    for splitted in splitter:
        if isinstance(splitted, str):
            yield splitted
        else:
            splitted['number'] = number_list(splitted['name'],
                                             splitted['number'],
                                             page_index)
            tag_dictionary[splitted['tag']] = (splitted['name'],
                                               splitted['number'])

            if splitted['name'] == 'header':
                yield template.render(**splitted, config=config)
            else:
                next_source = next(splitter)
                index = next_source.find('\n\n')
                if index == -1:
                    body, rest = next_source, ''
                else:
                    body, rest = next_source[:index], next_source[index + 2:]

                md = Markdown(extensions=['markdown.extensions.tables',
                                          'markdown.extensions.fenced_code'])
                body = md.convert(body)

                yield template.render(**splitted, body=body, config=config)
                if rest:
                    yield rest

    return tag_dictionary


def number_list(name, number, page_index=None):
    if page_index:
        if name == 'header':
            number = page_index + number[1:]
        else:
            number = page_index + number
    return number


def split_tag(text):
    """
    Split a tag from `text`. Tag is

    Parameters
    ----------
    text : str
        header text

    Examples
    --------
    >>> split_tag('{tag} text')
    ('text', 'tag')
    >>> split_tag('text')
    ('text', '')
    """
    m = re.search('\{.+?\}', text)
    if not m:
        return text, ''
    else:
        tag = m.group()
        return text.replace(tag, '').strip(), tag[1:-1]


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
    re_compile = re.compile(r'^(#+)(\S*?) (.+?)$', re.MULTILINE)
    number = {'header': [0] * 6}
    header_name = {'': 'header'}
    for key in config['kind']:
        number[key] = [0] * 6
        header_name[key[:3].lower()] = key
    cursor = 0

    while True:
        m = re_compile.search(source)
        if m:
            start, end = m.span()
            cursor += start
            if start:
                markdown = source[:start].strip()
                if markdown:
                    yield markdown
            name = header_name[m.group(2)[:3].lower()]
            depth = len(m.group(1)) - 1
            number[name][depth] += 1
            number[name][depth + 1:] = [0] * (len(number[name]) - depth)
            title, tag = split_tag(m.group(3))
            yield {'name': name, 'number': number[name][:depth + 1],
                   'title': title, 'tag': tag, 'cursor': cursor}
            source = source[end:]
            cursor += end
        else:
            markdown = source.strip()
            if markdown:
                yield markdown
            break

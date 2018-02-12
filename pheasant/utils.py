import codecs
import os
import re

import nbformat


def read_source(source: str):
    """
    Read markdown source string from file system.

    If `source` is not an existing filename, `source` itself is
    returned, assuming it is a markdown string.

    File encoding must be UTF-8. New line character is converted into LF.

    Parameters
    ----------
    source : str
        Markdown source filename or markdown string.

    Returns
    ------
    str : Markdown string.
    """
    if len(source) < 256 and os.path.exists(source):
        with codecs.open(source, 'r', 'utf8') as file:
            source = file.read()
            source = source.replace('\r\n', '\n').replace('\r', '\n')
    return source


def escaped_splitter_join(pattern: str,
                          pattern_escape: str,
                          source: str,
                          option=re.MULTILINE,
                          option_escape=re.MULTILINE | re.DOTALL):
    """Join escaped string with normal string."""
    text = ''
    for splitted in escaped_splitter(pattern, pattern_escape, source,
                                     option, option_escape):
        if isinstance(splitted, str):
            text += splitted
        else:
            yield text
            yield splitted
            text = ''
    if text:
        yield text


def escaped_splitter(pattern: str,
                     pattern_escape: str,
                     source: str,
                     option=re.MULTILINE,
                     option_escape=re.MULTILINE | re.DOTALL):
    for splitted in splitter(pattern_escape, source, option_escape):
        if not isinstance(splitted, str):
            yield splitted.group()
        else:
            yield from splitter(pattern, splitted, option)


def splitter(pattern: str, source: str, option=re.MULTILINE):
    """Generate splitted text from `source` by `pattern`."""
    re_compile = re.compile(pattern, option)

    while True:
        m = re_compile.search(source)
        if m:
            start, end = m.span()
            if start:
                yield source[:start]
            yield m
            source = source[end:]
        else:
            yield source
            break


def read(root: str, filename: str):
    """Utility function to read a file under `tests` directory."""
    root = os.path.dirname(os.path.abspath(root))

    basename = None
    while basename != 'tests':
        root, basename = os.path.split(root)
        if basename == '':
            raise ValueError('Could not find `tests` directory.', root)

    path = os.path.join(root, basename, 'resources', filename)
    path = os.path.abspath(path)

    with open(path) as f:
        if path.endswith('.ipynb'):
            return nbformat.read(f, as_version=4)
        else:
            return f.read()


def delete_cr(root):
    """CRLF -> LF.

    Usage:
        python -c "from pheasant.utils import delete_cr;delete_cr('.')"
    """
    def valid(path):
        ext = os.path.splitext(path)[1][1:]
        if ext in ['py', 'md', 'yml', 'css', 'in', 'cfg', 'json', 'jinja2']:
            return True

    def iterfiles():
        for path, dirs, files in os.walk(root):
            for fn in files:
                if valid(fn):
                    yield os.path.join(path, fn)

    for path in iterfiles():
        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
        text = text.replace('\r', '')
        with open(path, 'wb') as file:
            file.write(text.encode('utf-8'))

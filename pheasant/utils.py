import codecs
import os
import re

import nbformat


def read_source(source):
    if os.path.exists(source):
        with codecs.open(source, 'r', 'utf8') as file:
            source = file.read()
            source = source.replace('\r\n', '\n').replace('\r', '\n')
    return source


def splitter(pattern: str, source: str, option=re.MULTILINE):
    """
    Generate splitted text from `source` by `pattern`.
    """
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


def read(root, filename):
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

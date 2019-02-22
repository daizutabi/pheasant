import codecs
import os
from typing import Generator


def read_source(source: str) -> str:
    """Read markdown source string from file system.

    If `source` is not an existing filename, `source` itself is
    returned, assuming it is a markdown string.

    File encoding must be UTF-8. New line character is converted into LF.

    Parameters
    ----------
    source : str
        Markdown source filename or markdown string.

    Returns
    ------
    str
        Markdown string.
    """
    if len(source) < 256 and os.path.exists(source):
        with codecs.open(source, 'r', 'utf8') as file:
            source = file.read()
            source = source.replace('\r\n', '\n').replace('\r', '\n')
    return source


def read(root: str, filename: str) -> str:
    """Utility function to read a file under `tests` directory."""
    root = os.path.dirname(os.path.abspath(root))

    basename = ''
    while basename != 'tests':
        root, basename = os.path.split(root)
        if basename == '':
            raise ValueError('Could not find `tests` directory.', root)

    path = os.path.join(root, basename, 'resources', filename)
    path = os.path.abspath(path)

    with open(path) as f:
        return f.read()


# def delete_cr(root: str) -> None:
#     """CRLF -> LF.
#
#     Usage:
#         python -c "from pheasant.utils import delete_cr;delete_cr('.')"
#     """
#
#     def valid(path: str) -> bool:
#         ext = os.path.splitext(path)[1][1:]
#         if ext in ['py', 'md', 'yml', 'css', 'in', 'cfg', 'json', 'jinja2']:
#             return True
#         else:
#             return False
#
#     def iterfiles() -> Generator[str, None, None]:
#         for path, dirs, files in os.walk(root):
#             for fn in files:
#                 if valid(fn):
#                     yield os.path.join(path, fn)
#
#     for path in iterfiles():
#         with open(path, 'r', encoding='utf-8') as file_text:
#             text = file_text.read()
#         text = text.replace('\r', '')
#         with open(path, 'wb') as file_binary:
#             file_binary.write(text.encode('utf-8'))

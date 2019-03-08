import codecs
import os


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
        with codecs.open(source, "r", "utf8") as file:
            source = file.read()
            source = source.replace("\r\n", "\n").replace("\r", "\n")
    return source


def read(root: str, filename: str) -> str:
    """Utility function to read a file under `tests` directory."""
    root = os.path.dirname(os.path.abspath(root))

    basename = ""
    while basename != "tests":
        root, basename = os.path.split(root)
        if basename == "":
            raise ValueError("Could not find `tests` directory.", root)

    path = os.path.join(root, basename, "resources", filename)
    path = os.path.abspath(path)

    with open(path) as f:
        return f.read()

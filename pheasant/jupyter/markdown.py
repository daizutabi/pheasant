from ..markdown.splitter import (fenced_code_splitter,
                                 fenced_code_splitter_with_class)
from .config import config
from .exporter import export, inline_export, new_code_cell, run_and_export
from .preprocess import preprocess_code, preprocess_markdown


def convert(source: str):
    """Convert markdown string into markdown with running results.

    Parameters
    ----------
    source : str
        Markdown source string.

    Returns
    -------
    results : str
        Markdown source
    """
    config['run_counter'] = 0  # used in the cache module. MOVE!!
    sources = [source.strip() for source in cell_runner(source)]
    return '\n\n'.join(source for source in sources if source)


def cell_runner(source: str):
    """Generate markdown string with outputs after running the source.

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    str
        Markdown string.
    """
    for splitted in fenced_code_splitter(source):
        if isinstance(splitted, str):
            yield preprocess_markdown(splitted)
        else:
            language, source, options = splitted
            cell = new_code_cell(source, language=language, options=options)

            if 'inline' in options:
                cell.source = preprocess_code(cell.source)
                yield run_and_export(cell, inline_export)
            else:
                source = run_and_export(cell, export)
                yield from fenced_code_splitter_with_class(source)

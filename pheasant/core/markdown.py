import re

import nbformat


def new_notebook(source: str, language='python', metadata=None):
    """
    Convert a markdown source with `jupyter` fenced code into a markdown source
    with `python` fenced code after executing the jupyter codes.

    Parameters
    ----------
    source : str
        Markdwn source string.
    language : str, optional
        Fenced code language
    metadata: dict, optional
        Notebook metadata.
    """
    cells = []
    for cell in fenced_code_splitter(source, 'jupyter'):
        if isinstance(cell, str):
            cell = nbformat.v4.new_markdown_cell(cell)
            cells.append(cell)
        else:
            code, option = cell
            cell = nbformat.v4.new_code_cell(code)
            if option:
                options = [option.strip() for option in option.split(',')]
            else:
                options = []
            cell.metadata['pheasant'] = options
            cells.append(cell)

    if metadata is None:
        metadata = {'language_info': {'name': language}}

    # metadata = {
    #     "kernelspec": {
    #         "display_name": "Python 3",
    #         "language": "python",
    #         "name": "python3"
    #     },
    #     "language_info": {
    #         "codemirror_mode": {
    #             "name": "ipython",
    #             "version": 3
    #         },
    #         "file_extension": ".py",
    #         "mimetype": "text/x-python",
    #         "name": "python",
    #         "nbconvert_exporter": "python",
    #         "pygments_lexer": "ipython3",
    #         "version": "3.6.3"
    #     }
    # }

    return nbformat.v4.new_notebook(cells=cells, metadata=metadata)


def fenced_code_splitter(source: str, language: str):
    """
    Generate splitted markdown and jupyter notebook cell form `source`.
    The type of generated value is str or tuple.
    If str, it is markdown. If tuple, it is (code, option).
    Here, the option is a string after '```python'.
    """
    pattern = r'^```{}([^\n.]*)\n(.*?)\n^```$'.format(language)
    re_compile = re.compile(pattern, re.DOTALL | re.MULTILINE)

    while True:
        m = re_compile.search(source)
        if m:
            start, end = m.span()
            if start:
                markdown = source[:start].strip()
                if markdown:
                    yield markdown
            yield m.group(2).strip(), m.group(1).strip()
            source = source[end:]
        else:
            markdown = source.strip()
            if markdown:
                yield markdown
            break

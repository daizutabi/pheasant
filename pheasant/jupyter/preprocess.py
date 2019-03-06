"""Execute `{{expr}}` in a markdown source or fenced code.

If `expr` starts with '#', `expr` is not executed: {{#abc}} -> {{abc}}.
If `expr` starts with '^', `expr` is converted into a HTML source after
execution.

Above settings is default values and configurable.
"""

import re
from typing import Match

import nbformat
from nbformat import NotebookNode

from pheasant.jupyter.client import run_cell
from pheasant.jupyter.config import config
from pheasant.jupyter.renderer import inline_render, run_and_render
from pheasant.number import config as config_number


def preprocess_fenced_code(source: str) -> str:
    def replace_(match: Match) -> str:
        return replace(match.group(1), ignore_equal=True)

    return re.sub(config['inline_pattern'], replace_, source)


def preprocess_markdown(source: str) -> str:
    if source[:3] in ['```', '~~~', '<di']:  # escaped or already converted.
        return source

    def replace_and_run(match: Match) -> str:
        source = match.group(1)
        if source.startswith(config['inline_ignore_character']):
            return match.group().replace(source, source[1:])
        elif source.startswith(config['inline_display_character']):
            display = True
            source = source[1:]
        else:
            display = False

        source = replace(source)
        cell = nbformat.v4.new_code_cell(source)

        return run_and_render(cell, inline_render, display=display,
                              callback=update_extra_resources)

    source = move_from_header(source)  # Allows an inline expr in a header.
    return re.sub(config['inline_pattern'], replace_and_run, source)


def replace(source: str, ignore_equal: bool = False) -> str:
    """Replace a match object with `display` function.

    Parameters
    ----------
    source
        The matched source given by the `re.sub` function for an inline cell.
    ignore_equal
        If True, do not replace the source which contains `=`.

    Returns
    -------
    str
        Replaced python source code but has not been executed yet.
    """
    convert = 'pheasant.jupyter.display'

    if '=' in source and not ignore_equal:
        return source

    if source.startswith(config['inline_html_character']):
        source = source[1:]
        output = 'html'
    else:
        output = 'markdown'

    if ';' in source:
        sources = source.split(';')
        source = '_pheasant_dummy'
        sources[-1] = f'{source} = {sources[-1]}'
        run_cell('\n'.join(sources))

    return f'{convert}({source}, output="{output}")'


def update_extra_resources(cell: NotebookNode) -> None:
    """Update extra resources in the pheasant config.

    If the `text/plain` output of the cell is `tuple`,
    the first element is the real output of the cell execution
    and the second element is a dictionary to update the extra
    resources in the pheasant config.

    Parameters
    ----------
    cell
        Input cell after execution.
    """
    def replace(data: NotebookNode) -> None:
        display = eval(data['text/plain'])
        if isinstance(display, tuple):
            html, resources = display
            update(resources)
            data['text/html'] = html
            del data['text/plain']

    def update(resources: dict) -> None:
        from pheasant.config import config as pheasant_config

        source_file = pheasant_config['source_file']
        if source_file is None:
            config = pheasant_config
        else:
            extra_resources = pheasant_config['extra_resources']
            if source_file not in extra_resources:
                extra_resources[source_file] = {}
            config = extra_resources[source_file]

        extra_keys = ['extra_css', 'extra_raw_css',
                      'extra_javascript', 'extra_raw_javascript']

        for key in extra_keys:
            if key not in config:
                config[key] = []
            if key in resources:
                values = [value for value in resources[key]
                          if value not in config[key]]
                if values:
                    config[key].extend(values)

    for output in cell.outputs:
        if (output['output_type'] == 'execute_result'
                and 'text/plain' in output['data']):
            replace(output['data'])


def move_from_header(source: str) -> str:
    """Inline cells are moved below header line.

    Before:
        #Fig title {{plot}}

    After:
        #Fig title
        <!-- begin -->
        {{plot}}
        <!-- end -->
    """
    begin = config_number['begin_pattern']
    end = config_number['end_pattern']

    def replace(match):
        header, inline, _, title = match.groups()
        header = header.strip()
        title = title.strip()
        if title:
            return f'{header} {title}\n{begin}\n{inline}\n{end}'
        else:
            return f'{header}\n{begin}\n{inline}\n{end}'

    pattern = r'^(#.*?)(' + config['inline_pattern'] + r')(.*?)$'
    return re.sub(pattern, replace, source, flags=re.MULTILINE)

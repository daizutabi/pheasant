"""Execute `{{expr}}` in a markdown source or fenced code.

If `expr` starts with '#', `expr` is not executed: {{#abc}} -> {{abc}}.
If `expr` starts with '^', `expr` is converted into a HTML source after
execution.

Above settings is default values and configurable.
"""

import re
from typing import Match

from pheasant.jupyter.client import execute
from pheasant.jupyter.config import config
from pheasant.jupyter.renderer import execute_and_render, render_inline_code
from pheasant.number import config as config_number


def preprocess_fenced_code(code: str) -> str:
    def replace_(match: Match) -> str:
        return replace(match.group(1), ignore_equal=True)

    return re.sub(config['inline_pattern'], replace_, code)


def preprocess_markdown(code: str) -> str:
    if code[:3] in ['```', '~~~', '<di']:  # escaped or already converted.
        return code

    def replace_and_run(match: Match) -> str:
        code = match.group(1)
        if code.startswith(config['inline_ignore_character']):
            return match.group().replace(code, code[1:])
        elif code.startswith(config['inline_display_character']):
            display = True
            code = code[1:]
        else:
            display = False

        code = replace(code)
        return execute_and_render(code, render_inline_code, language='python',
                                  callback=update_extra_resources,
                                  display=display)

    code = move_from_header(code)  # Allows an inline expr in a header.
    return re.sub(config['inline_pattern'], replace_and_run, code)


def replace(code: str, ignore_equal: bool = False) -> str:
    """Replace a match object with `display` function.

    Parameters
    ----------
    code
        The matched code given by the `re.sub` function for an inline cell.
    ignore_equal
        If True, do not replace the code which contains `=`.

    Returns
    -------
    str
        Replaced python code code but has not been executed yet.
    """
    if '=' in code and not ignore_equal:
        return code

    if code.startswith(config['inline_html_character']):
        code = code[1:]
        output = 'html'
    else:
        output = 'markdown'

    if ';' in code:
        codes = code.split(';')
        code = '_pheasant_dummy'
        codes[-1] = f'{code} = {codes[-1]}'
        execute('\n'.join(codes))

    return f'pheasant.jupyter.display.display({code}, output="{output}")'


def update_extra_resources(outputs: list) -> None:
    """Update extra resources in the pheasant config.

    If the `text/plain` output of the cell is `tuple`,
    the first element is the real output of the cell execution
    and the second element is a dictionary to update the extra
    resources in the pheasant config.

    Parameters
    ----------
    outputs
        Outputs of code execution.
    """
    def replace(data: dict) -> None:
        """Replace tuple output to html and register extra resources."""
        display = eval(data['text/plain'])
        if isinstance(display, tuple):
            html, resources = display
            update(resources)
            data['text/html'] = html
            del data['text/plain']

    def update(resources: dict) -> None:
        """Update extra resources.

        If `source_file` is not specified, global extra_XXXs are updated,
        Otherwise, config['extre_resources'][<source_file>] updated.
        """

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

    for output in outputs:
        if (output['type'] == 'execute_result'
                and 'text/plain' in output['data']):
            replace(output['data'])


def move_from_header(code: str) -> str:
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
    return re.sub(pattern, replace, code, flags=re.MULTILINE)

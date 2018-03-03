from typing import Any, Dict

config: Dict[str, Any] = {
    # Notebook format version as argument of nbformat.read function.
    'format_version': 4,

    # Jinja2 template file for Notebook conversion.
    'template_file': 'output_text_outside.jinja2',

    # Jinja2 template file for inline code.
    'inline_template_file': 'inline.jinja2',

    # Jupyter kernel time-out period in second.
    'timeout': 600,

    # Jupyter kernel names (key: language, value: kernel name).
    'kernel_name': {
        'python': 'python3'
    },

    # Inline code pattern for inline evaluation.
    'inline_pattern': r'\{\{(.+?)\}\}',

    # Character to convert markdown into html in an inline code.
    'inline_html_character': '^',

    # Character to ignore an inline code.
    'inline_ignore_character': '#',

    # Extra package directories that will be added to sys.path.
    'sys_paths': [],

    # Extra modules that will be imported.
    'import_modules': [],

    # Markdown Extension to render header title and inline code.
    'markdown_extensions': [],

    # Initializing code
    'init_codes': [],

    # Modules imported programmatically by jupyter converter.
    # Dont't Edit.
    'modules': {},

    # Time that module was imported. (Not implemented.)
    # Dont't Edit.
    'module_imported_time': {},
    'matplotlib_format': 'png',
    'bokeh_format': 'html',
    'holoviews_backend': 'bokeh',
}

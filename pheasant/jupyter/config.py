config = {
    # Notebook format version as argument of nbformat.read function.
    'format_version': 4,

    # Jinja2 template file for Notebook conversion.
    'template_file': 'output_text_inside.jinja2',

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

    # Source code pattern for quotation of code from file.
    'code_pattern': r'^#Code (.+?)$',

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

    # Cache for source code to run.
    # Dont't Edit.
    'cell_source_cache': {},

    # Time that module was imported. (Not implemented.)
    # Dont't Edit.
    'module_imported_time': {}
}

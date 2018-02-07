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

    # Source code pattern for quotation of code from file.
    'code_pattern': r'^#Code (.+?)$',

    # Output format: markdown or notebook.
    'output_format': 'markdown',

    # Extra package directories that will be added to sys.path.
    'package_dirs': [],

    # Extra packages that will be imported.
    'packages': [],

    # Initializing code
    'init_codes': [],

    # Modules imported programmatically by jupyter converter.
    'modules': {},
}

config = {
    # Notebook format version as argument of nbformat.read function.
    'format_version': 4,

    # Jinja2 template file for Notebook conversion.
    'template_file': 'output_text_inside.jinja2',

    # Jupyter kernel time-out period in second.
    'timeout': 600,

    # Jupyter kernel names (key: language, value: kernel name).
    'kernel_name': {
        'python': 'python3'
    },

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

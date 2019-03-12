from typing import Any, Dict

config: Dict[str, Any] = {
    # Jinja2 template file for fenced code.
    "fenced_code_template_file": "fenced_code.jinja2",
    # Jinja2 template file for inline code.
    "inline_code_template_file": "inline_code.jinja2",
    # Jinja2 template file for escaped code.
    "escaped_code_template_file": "escaped_code.jinja2",
    # Jupyter kernel names (key: language, value: kernel name).
    "kernel_name": {"python": "python3"},
    # Character to convert markdown into html in an inline code.
    "inline_html_character": "^",
    # Character to ignore an inline code.
    "inline_ignore_character": "#",
    # Character to display an inline code.
    "inline_display_character": "!",
    # Extra package directories that will be added to sys.path.
    "extra_paths": [],
    # Extra modules that will be imported.
    "extra_modules": ['pheasant.jupyter.display'],
    # Markdown Extension to render header title and inline code.
    "markdown_extensions": [],
    # Initializing code
    "init_codes": [],
    # Modules imported programmatically by jupyter converter.
    # Dont't Edit.
    "modules": {},
    # Time that module was imported. (Not implemented.)
    # Dont't Edit.
    "module_imported_time": {},
    # Format and backend.
    "matplotlib_format": "png",
    "bokeh_format": "html",
    "holoviews_backend": "bokeh",
}

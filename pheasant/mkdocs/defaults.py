try:
    from mkdocs import utils
    from mkdocs.config import config_options
except ImportError:
    DEFAULT_SCHEMA = ()
else:
    DEFAULT_SCHEMA = (
        ('output_format', config_options.Type(
            utils.string_types, default='html')),
        ('template_file', config_options.Type(
            utils.string_types, default='')),
        ('kernel_name', config_options.Type(
            dict, default={'python', 'python3'})),
    )

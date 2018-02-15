__version__ = '0.4.0'

try:  # For import from jupyter kernel.
    from .converters import convert
except ImportError:
    pass

try:  # For pelican plugin.
    from .plugins.pelican import register
except ImportError:
    pass

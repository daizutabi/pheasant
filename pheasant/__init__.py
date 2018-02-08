__version__ = '0.3.0'

try:  # For import from jupyter kernel.
    from .converters import convert
except ImportError:
    pass

try:
    from .plugins.pelican import register
except ImportError:
    pass

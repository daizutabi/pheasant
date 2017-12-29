__version__ = '0.1.0'

from .converters import convert

try:
    from .plugins.pelican import register
except ImportError:
    pass

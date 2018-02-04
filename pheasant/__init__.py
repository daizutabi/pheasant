__version__ = '0.3.0'

from .converters import convert

try:
    from .plugins.pelican import register
except ImportError:
    pass

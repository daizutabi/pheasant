__version__ = '0.2.1'

from .converters import convert

try:
    from .plugins.pelican import register
except ImportError:
    pass

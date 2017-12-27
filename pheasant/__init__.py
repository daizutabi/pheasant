__version__ = '0.1.0'

try:
    from .plugins.pelican import register
except ImportError:
    pass

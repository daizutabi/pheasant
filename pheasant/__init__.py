__version__ = '0.1.0'

from pheasant.core.convert import convert
from pheasant.config import config

try:
    from .plugins.pelican import register
except ImportError:
    pass

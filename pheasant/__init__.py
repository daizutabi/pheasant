__version__ = '0.1.0'


from pheasant.config import config
from pheasant.core import convert, set_config

try:
    from .plugins.pelican import register
except ImportError:
    pass

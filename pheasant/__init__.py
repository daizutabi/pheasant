__version__ = '0.3.0'

try:  # For import from jupyter kernel.
    from .converters import convert
except ImportError:
    pass

try:
    from .plugins.pelican import register
except ImportError:
    pass


# test

import logging
logger = logging.getLogger('pheasant')
stream = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)-7s -  [Pheasant] %(message)s ")
stream.setFormatter(formatter)
logger.addHandler(stream)
logger.setLevel('INFO')

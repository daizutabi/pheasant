__version__ = '1.0.1'

# import logging

try:  # For import from jupyter kernel.
    from pheasant.converters import convert
except ImportError:
    pass


__all__ = ['convert', 'register']

# Test
# logger = logging.getLogger('pheasant')
# stream = logging.StreamHandler()
# formatter = logging.Formatter("%(levelname)-7s -  [Pheasant] %(message)s ")
# stream.setFormatter(formatter)
# logger.addHandler(stream)
# logger.setLevel('INFO')

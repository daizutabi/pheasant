__version__ = '1.0.1'


# THIS IS NEEDED! For import from jupyter kernel inside.
try:
    from pheasant.converters import convert
except ImportError:
    pass


__all__ = ['convert']

# Test
# logger = logging.getLogger('pheasant')
# stream = logging.StreamHandler()
# formatter = logging.Formatter("%(levelname)-7s -  [Pheasant] %(message)s ")
# stream.setFormatter(formatter)
# logger.addHandler(stream)
# logger.setLevel('INFO')

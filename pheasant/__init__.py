__version__ = '1.0.2'


# THIS IS NEEDED! For import from jupyter kernel inside.
try:
    from pheasant.converters import convert
except ImportError:
    pass


__all__ = ['convert']

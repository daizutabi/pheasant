from typing import Callable, Optional, Union

try:
    import sympy
except ImportError:
    sympy = None


def subscript(var: str, sub: Union[str, int]) -> str:
    if '{_}' not in var:
        var += '{_}'
    return var.replace('{_}', '_{' + str(sub) + '}')


def row(var: str, r: int, c: Optional[int] = None,
        transpose: bool = False) -> str:
    if c is None:
        c = r
        sub = '{i}'
    else:
        sub = '{i}{r}' if transpose else '{r}{i}'
    return '&'.join(subscript(var, sub.format(r=r, i=i))
                    for i in range(1, c + 1))


def matrix(var: str, nrows: int, ncols: int, transpose: bool = False) -> str:
    align = 'c' * ncols
    mat = '\\\\'.join([row(var, i, ncols, transpose)
                       for i in range(1, nrows + 1)])
    return '\n'.join([
        R'\left[\begin{array}{' + align + '}',
        mat,
        R'\end{array}\right]'
    ])


def sympy_matrix(var: str, n: int, m: int) -> sympy.Matrix:
    matrix = [[sympy.symbols(f'{var}_{i}{j}') for j in range(1, m + 1)]
              for i in range(1, n + 1)]
    return sympy.Matrix(matrix)


def const(value, nrows: int, ncols: Optional[int] = None) -> str:
    if ncols is None:
        nrows, ncols = 1, nrows
    align = 'c' * ncols
    row = '&'.join([str(value)] * ncols)
    mat = '\\\\'.join([row] * nrows)
    return '\n'.join([
        R'\left[\begin{array}{' + align + '}',
        mat,
        R'\end{array}\right]'
    ])


def ones(nrows: int, ncols: Optional[int] = None) -> str:
    return const(1, nrows, ncols)


def zeros(nrows: int, ncols: Optional[int] = None) -> str:
    return const(0, nrows, ncols)


def vector(var: str, length: int, transpose: bool = False) -> str:
    vec = row(var, length)
    if transpose:
        align = 'c' * length
        vec = vec.replace('&', '\\\\')
    else:
        align = 'c' * length
    return '\n'.join([
        R'\left[\begin{array}{' + align + '}',
        vec,
        R'\end{array}\right]'
    ])


def partial(f: str, x: str, frac: bool = False) -> str:
    if frac:
        return (R'\frac{\partial ' + f + R'}{\partial\mathbf{'
                + x.upper() + '}}')
    else:
        return (R'\partial ' + f + R'/\partial\mathbf{'
                + x.upper() + '} ')


class Matrix:
    def __init__(self, var: str, nrows: int, ncols: int):
        self.var = var
        self.nrows = nrows
        self.ncols = ncols

    def __str__(self) -> str:
        return matrix(self.var, self.nrows, self.ncols)

    @property
    def T(self) -> str:
        return matrix(self.var, self.ncols, self.nrows, transpose=True)

    @property
    def S(self) -> sympy.Matrix:
        return sympy_matrix(self.var, self.nrows, self.ncols)

    def apply(self, func: Callable) -> sympy.Matrix:
        mat = self.S
        vec = sympy.Matrix([[func(x) for x in mat]])
        return vec.reshape(self.nrows, self.ncols)

    @property
    def shape(self) -> tuple:
        return (self.nrows, self.ncols)

    def partial(self, f: str, frac: bool = False) -> str:
        if frac:
            var = R'\frac{\partial ' + f + R'}{\partial ' + self.var + '{_} }'
        else:
            var = R'\partial ' + f + R'/\partial ' + self.var + '{_} '
        return matrix(var, self.nrows, self.ncols)

    def spartial(self, f: str, frac: bool = False) -> str:
        return partial(f, self.var, frac)


class Vector:
    def __init__(self, var: str, length: int):
        self.var = var
        self.length = length

    def __str__(self) -> str:
        return vector(self.var, self.length)

    @property
    def T(self) -> str:
        return vector(self.var, self.length, transpose=True)

    @property
    def S(self) -> sympy.Matrix:
        return sympy_matrix(self.var, 1, self.length)

    @property
    def shape(self) -> tuple:
        return (self.length,)

    def partial(self, f: 'str', frac: bool = False) -> str:
        if frac:
            var = R'\frac{\partial ' + f + R'}{\partial ' + self.var + '{_} }'
        else:
            var = R'\partial ' + f + R'/\partial ' + self.var + '{_} '
        return vector(var, self.length)

    def spartial(self, f: str, frac: bool = False) -> str:
        return partial(f, self.var, frac)

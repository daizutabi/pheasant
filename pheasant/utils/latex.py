from dataclasses import dataclass
from typing import Callable, Optional, Union

import sympy


def subscript(var: str, sub: Union[str, int]) -> str:
    if "{_}" not in var:
        var += "{_}"
    return var.replace("{_}", f"_{{{sub}}}")


def row(var: str, n: int, m: Optional[int] = None, transpose: bool = False) -> str:
    if m is None:
        m = n
        sub = "{i}"
    else:
        sub = "{i}{n}" if transpose else "{n}{i}"
    return "&".join(subscript(var, sub.format(n=n, i=i)) for i in range(1, m + 1))


def wrap_matrix(mat: str, delim: str = "[") -> str:
    if delim == "[":
        delim = "[]"
    elif delim == "(":
        delim = "()"
    else:
        raise ValueError("delim must be '(' or '['")
    return f"\\left{delim[0]}{mat}\\right{delim[1]}"


def begin(env: str, align: str) -> str:
    return f"\\begin{{{env}}}{{{align}}}"


def end(env: str) -> str:
    return f"\\end{{{env}}}"


def matrix(
    var: str,
    n: int,
    m: int,
    transpose: bool = False,
    delim: str = "[",
    env: str = "array",
) -> str:
    align = "c" * m
    mat = "\\\\\n".join([row(var, i, m, transpose) for i in range(1, n + 1)])
    mat = "\n".join([begin(env, align), mat, end(env)])
    return wrap_matrix(mat, delim)


def sympy_matrix(var: str, n: int, m: int) -> sympy.Matrix:
    if n == 0:
        matrix = [[sympy.symbols(f"{var}_{j}") for j in range(1, m + 1)]]
    elif m == 0:
        matrix = [[sympy.symbols(f"{var}_{i}")] for i in range(1, n + 1)]
    else:
        matrix = [
            [sympy.symbols(f"{var}_{i}{j}") for j in range(1, m + 1)]
            for i in range(1, n + 1)
        ]
    return sympy.Matrix(matrix)


def const(
    value, n: int, m: Optional[int] = None, delim: str = "[", env: str = "array"
) -> str:
    if m is None:
        n, m = 1, n
    align = "c" * m
    row = "&".join([str(value)] * m)
    mat = "\\\\\n".join([row] * n)
    mat = "\n".join([begin(env, align), mat, end(env)])
    return wrap_matrix(mat, delim)


def ones(n: int, m: Optional[int] = None, delim: str = "[") -> str:
    return const(1, n, m, delim)


def zeros(n: int, m: Optional[int] = None, delim: str = "[") -> str:
    return const(0, n, m, delim)


def vector(
    var: str, n: int, transpose: bool = False, delim: str = "[", env: str = "array"
) -> str:
    vec = row(var, n)
    if transpose:
        align = "c"
        vec = vec.replace("&", "\\\\")
    else:
        align = "c" * n
    vec = "\n".join([begin(env, align), vec, end(env)])
    return wrap_matrix(vec, delim)


def partial(f: str, x: str, frac: bool = False) -> str:
    if frac:
        return f"\\frac{{\\partial {f}}}{{\\partial {x}}}"
    else:
        return f"\\partial {f}/\\partial {x}"


@dataclass
class Expression:
    expr: str

    def _repr_latex_(self) -> str:
        return self.expr


@dataclass
class Base:
    var: str
    n: int
    m: int = 0
    _symbol: str = ""
    transpose: bool = False
    delim: str = "["
    env: str = "array"

    def __post_init__(self):
        if not self._symbol:
            self._symbol = f"\\mathbf{{{self.var.upper()}}}"

    @property
    def symbol(self):
        return Expression(self._symbol)

    def spartial(self, f: str, frac: bool = True) -> Expression:
        return Expression(partial(f, self._symbol, frac))


@dataclass
class Matrix(Base):
    def _repr_latex_(self) -> str:
        return matrix(self.var, self.n, self.m, self.transpose, self.delim, self.env)

    @property
    def T(self) -> "Matrix":
        return Matrix(
            self.var,
            self.m,
            self.n,
            transpose=not self.transpose,
            delim=self.delim,
            env=self.env,
        )

    @property
    def S(self) -> sympy.Matrix:
        return sympy_matrix(self.var, self.n, self.m)

    def apply(self, func: Callable) -> sympy.Matrix:
        mat = self.S
        vec = sympy.Matrix([[func(x) for x in mat]])
        return vec.reshape(self.n, self.m)

    @property
    def shape(self) -> tuple:
        return (self.n, self.m)

    def partial(self, f: str, frac: bool = False) -> "Matrix":
        var = partial(f, self.var + "{_}", frac)
        return Matrix(
            var,
            self.n,
            self.m,
            transpose=self.transpose,
            delim=self.delim,
            env=self.env,
        )


@dataclass
class Vector(Base):
    def _repr_latex_(self) -> str:
        return vector(self.var, self.n, self.transpose, self.delim, self.env)

    @property
    def T(self) -> "Vector":
        return Vector(
            self.var,
            self.n,
            transpose=not self.transpose,
            delim=self.delim,
            env=self.env,
        )

    @property
    def S(self) -> sympy.Matrix:
        if self.transpose:
            return sympy_matrix(self.var, self.n, 0)
        else:
            return sympy_matrix(self.var, 0, self.n)

    @property
    def shape(self) -> tuple:
        return (self.n,)

    def partial(self, f: "str", frac: bool = False) -> "Vector":
        var = partial(f, self.var + "{_}", frac)
        return Vector(
            var, self.n, transpose=self.transpose, delim=self.delim, env=self.env
        )

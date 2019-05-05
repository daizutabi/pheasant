import pytest
import sympy

from pheasant.utils import latex as L


def test_subscript():
    assert L.subscript("x", 2) == "x_{2}"
    assert L.subscript("x", "i") == "x_{i}"


def test_row():
    assert L.row("r", 2) == "r_{1}&r_{2}"
    assert L.row("r", 2, 3) == "r_{21}&r_{22}&r_{23}"
    assert L.row("r", 2, 3, transpose=True) == "r_{12}&r_{22}&r_{32}"


def test_matrix():
    m = L.matrix("m", 1, 2)
    assert m == "\\left[\\begin{array}{cc}\nm_{11}&m_{12}\n\\end{array}\\right]"
    m = L.matrix("m", 1, 2, transpose=True, mat_delim="(")
    assert m == "\\left(\\begin{array}{cc}\nm_{11}&m_{21}\n\\end{array}\\right)"
    with pytest.raises(ValueError):
        L.matrix("m", 1, 2, transpose=True, mat_delim="<")


def test_sympy_matrix():
    assert isinstance(L.sympy_matrix("m", 1, 2), sympy.Matrix)


def test_const():
    assert L.ones(2, 1) == "\\left[\\begin{array}{c}\n1\\\\\n1\n\\end{array}\\right]"
    assert L.zeros(1, 2) == "\\left[\\begin{array}{cc}\n0&0\n\\end{array}\\right]"


def test_vector():
    answer = "\\left[\\begin{array}{cc}\nv_{1}&v_{2}\n\\end{array}\\right]"
    assert L.vector("v", 2) == answer
    assert L.zeros(1, 2) == "\\left[\\begin{array}{cc}\n0&0\n\\end{array}\\right]"
    answer = "\\left[\\begin{array}{c}\nv_{1}\\\\v_{2}\n\\end{array}\\right]"
    assert L.vector("v", 2, transpose=True) == answer


def test_partial():
    assert L.partial("f", "x") == "\\partial f/\\partial\\mathbf{X}"
    assert L.partial("f", "x", frac=True) == "\\frac{\\partial f}{\\partial\\mathbf{X}}"


def test_matrix_class():
    m = L.Matrix("m", 2, 1)
    assert (
        repr(m) == "\\left[\\begin{array}{c}\nm_{11}\\\\\nm_{21}\n\\end{array}\\right]"
    )
    assert m.T == "\\left[\\begin{array}{cc}\nm_{11}&m_{21}\n\\end{array}\\right]"
    assert isinstance(m.S, sympy.Matrix)

    assert m.shape == (2, 1)

    answer = (
        "\\left[\\begin{array}{c}\n\\partial f/\\partial m_{11}\\\\\n"
        "\\partial f/\\partial m_{21}\n\\end{array}\\right]"
    )
    assert m.partial("f") == answer
    assert m.spartial("f") == "\\partial f/\\partial\\mathbf{M}"


def test_vector_class():
    v = L.Vector("v", 2)
    assert repr(v) == "\\left[\\begin{array}{cc}\nv_{1}&v_{2}\n\\end{array}\\right]"
    assert v.T == "\\left[\\begin{array}{c}\nv_{1}\\\\v_{2}\n\\end{array}\\right]"
    assert isinstance(v.S, sympy.Matrix)
    assert v.shape == (2,)

    answer = (
        "\\left[\\begin{array}{cc}\n\\partial f/\\partial v_{1}&\\partial f/"
        "\\partial v_{2}\n\\end{array}\\right]"
    )
    assert v.partial("f") == answer
    assert v.spartial("f") == "\\partial f/\\partial\\mathbf{V}"

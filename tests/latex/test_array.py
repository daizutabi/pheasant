from pheasant.latex.array import (
    Matrix,
    Vector,
    const,
    matrix,
    ones,
    partial,
    row,
    subscript,
    sympy_matrix,
    vector,
    zeros,
)


def test_subscript():
    assert subscript("a", 3) == "a_{3}"


def test_row():
    assert row("c", 3) == "c_{1}&c_{2}&c_{3}"
    assert row("c", 3, 4) == "c_{31}&c_{32}&c_{33}&c_{34}"
    assert row("c", 3, 4, True) == "c_{13}&c_{23}&c_{33}&c_{43}"


def test_matrix():
    latex = "\n".join(
        [
            r"\left[\begin{array}{ccc}",
            r"a_{11}&a_{12}&a_{13}\\a_{21}&a_{22}&a_{23}\\a_{31}&a_{32}&a_{33}",
            r"\end{array}\right]",
        ]
    )
    assert matrix("a", 3, 3) == latex


def test_sympy_matrix():
    answer = "Matrix([[a_11, a_12, a_13], [a_21, a_22, a_23]])"
    str(sympy_matrix("a", 2, 3)) == answer


def test_const():
    answer = "\\left[\\begin{array}{ccc}\n1&1&1\\\\1&1&1\n\\end{array}\\right]"
    const(1, 2, 3) == answer
    const("v", 3) == "\\left[\\begin{array}{ccc}\nv&v&v\n\\end{array}\\right]"


def test_ones():
    assert ones(2) == "\\left[\\begin{array}{cc}\n1&1\n\\end{array}\\right]"


def test_zeros():
    assert zeros(2) == "\\left[\\begin{array}{cc}\n0&0\n\\end{array}\\right]"


def test_vector():
    answer = "\\left[\\begin{array}{cc}\na_{1}&a_{2}\n\\end{array}\\right]"
    assert vector("a", 2) == answer
    answer = "\\left[\\begin{array}{cc}\na_{1}\\\\a_{2}\n\\end{array}\\right]"
    assert vector("a", 2, transpose=True) == answer


def test_partial():
    assert partial("f", "x") == "\\partial f/\\partial\\mathbf{X} "
    answer = "\\frac{\\partial f}{\\partial\\mathbf{X}}"
    assert partial("f", "x", frac=True) == answer


def test_matrix_class():
    m = Matrix("a", 2, 3)
    answer = (
        "\\left[\\begin{array}{ccc}\na_{11}&a_{12}&a_{13}"
        "\\\\a_{21}&a_{22}&a_{23}\n\\end{array}\\right]"
    )
    assert str(m) == answer

    answer = (
        "\\left[\\begin{array}{cc}\na_{11}&a_{21}\\\\a_{12}&a_{22}"
        "\\\\a_{13}&a_{23}\n\\end{array}\\right]"
    )
    assert m.T == answer
    assert str(m.S) == "Matrix([[a_11, a_12, a_13], [a_21, a_22, a_23]])"

    answer = "Matrix([[a_11**2, a_12**2, a_13**2]," " [a_21**2, a_22**2, a_23**2]])"
    assert str(m.apply(lambda x: x ** 2)) == answer

    assert m.shape == (2, 3)

    answer = (
        "\\left[\\begin{array}{ccc}\n\\partial f/\\partial a_{11} &"
        "\\partial f/\\partial a_{12} &\\partial f/\\partial a_{13} "
        "\\\\\\partial f/\\partial a_{21} &\\partial f/\\partial a_{22} "
        "&\\partial f/\\partial a_{23} \n\\end{array}\\right]"
    )
    assert m.partial("f") == answer

    answer = (
        "\\left[\\begin{array}{ccc}\n\\frac{\\partial f}"
        "{\\partial a_{11} }&\\frac{\\partial f}{\\partial a_{12} }"
        "&\\frac{\\partial f}{\\partial a_{13} }\\\\\\frac{\\partial f}"
        "{\\partial a_{21} }&\\frac{\\partial f}{\\partial a_{22} }&"
        "\\frac{\\partial f}{\\partial a_{23} }\n\\end{array}\\right]"
    )
    assert m.partial("f", frac=True) == answer

    assert m.spartial("f") == "\\partial f/\\partial\\mathbf{A} "
    answer = "\\frac{\\partial f}{\\partial\\mathbf{A}}"
    assert m.spartial("f", frac=True) == answer


def test_vector_class():
    v = Vector("a", 2)
    answer = "\\left[\\begin{array}{cc}\na_{1}&a_{2}\n\\end{array}\\right]"
    assert str(v) == answer

    answer = "\\left[\\begin{array}{cc}\na_{1}\\\\a_{2}\n" "\\end{array}\\right]"
    assert v.T == answer
    assert str(v.S) == "Matrix([[a_11, a_12]])"
    assert v.shape == (2,)

    answer = (
        "\\left[\\begin{array}{cc}\n\\partial f/\\partial a_{1} &"
        "\\partial f/\\partial a_{2} \n\\end{array}\\right]"
    )
    assert v.partial("f") == answer

    answer = (
        "\\left[\\begin{array}{cc}\n\\frac{\\partial f}"
        "{\\partial a_{1} }&\\frac{\\partial f}{\\partial a_{2} }\n"
        "\\end{array}\\right]"
    )
    assert v.partial("f", frac=True) == answer

    assert v.spartial("f") == "\\partial f/\\partial\\mathbf{A} "
    answer = "\\frac{\\partial f}{\\partial\\mathbf{A}}"
    assert v.spartial("f", frac=True) == answer

from pheasant.latex.array import matrix, row, subscript


def test_subscript():
    assert subscript('a', 3) == 'a_{3}'


def test_row():
    assert row('c', 3, 4) == 'c_{31}&c_{32}&c_{33}&c_{34}'
    assert row('c', 3, 4, True) == 'c_{13}&c_{23}&c_{33}&c_{43}'


def test_matrix():
    latex = '\n'.join([
        R'\left(\begin{array}{ccc}',
        R'a_{11}&a_{12}&a_{13}\\a_{21}&a_{22}&a_{23}\\a_{31}&a_{32}&a_{33}',
        R'\end{array}\right)',
    ])
    assert matrix('a', 3, 3) == latex

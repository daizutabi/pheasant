import pytest


@pytest.mark.parametrize("nl", ["\n", "\r\n"])
def test_format_text(script, nl):
    source = (
        "a=1\n\n# あいうえおかきく\n# けこabc def ghi jkl mno pqr"
        "さしすせそなにぬねのabc def\n# hij klm aaaaaaaaaaaaaaaaa\n"
    ).replace("\n", nl)
    answer = (
        "a=1\n\n# あいうえ\n# おかきく\n# けこabc\n# def ghi\n# jkl mno\n"
        "# pqrさし\n# すせそな\n# にぬねの\n# abc def\n# hij klm\n# aaaa"
        "aaaaaaaaaaaaa\n"
    ).replace("\n", nl)
    assert script.convert(source, 10) == answer
    answer = (
        "a=1\n\n# あいうえおかきくけこabc def ghi jkl mno pqrさしす\n# "
        "せそなにぬねのabc def hij klm aaaaaaaaaaaaaaaaa\n"
    ).replace("\n", nl)
    assert script.convert(source, 50) == answer

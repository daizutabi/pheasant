from pheasant.code.converter import initialize, convert


def test_convert():
    initialize()
    assert convert("abc") == "abc"

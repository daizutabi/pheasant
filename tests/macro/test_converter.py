from pheasant.macro.converter import initialize, convert


def test_initialize():
    assert initialize() is None


def test_convert():
    assert convert("abc") == "abc"
    assert convert("text\n[=abc]:ABC\n[=abc]text") == "text\nABCtext"

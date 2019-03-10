from pheasant.macro.converter import convert, initialize


def test_initialize():
    assert initialize() is None


def test_convert():
    assert convert("abc") == "abc"
    assert convert("text\n[=abc]:ABC\n[=abc]text") == "text\nABCtext"


def test_convert_inline_code():
    assert convert("text\n[=abc]:{{2*4}}\n[=abc]text") == "text\n8text"


def test_convert_comment():
    assert (
        convert("text\n[=#xyz]:{{2*4}}\n[=xyz]text") == "text\n[=xyz]:{{2*4}}\nXXXtext"
    )

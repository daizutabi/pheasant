import pytest


@pytest.fixture()
def convert(script):
    def func(source):
        return script.convert(source, max_line_length=88)

    return func


def test_python_parse_source(convert):
    source = "# # Title\n\n# ## Section\n"
    assert convert(source) == source
    source = "# # Title\n\n# abc\n# def\n# ghi\n"
    assert convert(source) == "# # Title\n\n# abc def ghi\n"
    assert convert("# あ\n# い\n# う\n") == "# あいう\n"
    assert convert("# あa\n# い\n# う\n") == "# あaいう\n"
    assert convert("# あa\n# bい\n#う\n") == "# あa bいう\n"
    assert convert("# あa\n# bい\n#う") == "# あa bいう\n"


def test_python_parse_code(convert):
    assert convert("# # Title\na=1\n") == "# # Title\na=1\n"
    assert convert("# # Title\n\na=1\n") == "# # Title\n\na=1\n"
    assert convert("# a\na=1\n") == "# a\na=1\n"


def test_python_parse_code_escaped(convert):
    source = "# a\n# ~~~\n# abc\n# ~~~\na=1\n"
    assert convert(source) == "# a\n# ~~~\n# abc\n# ~~~\na=1\n"

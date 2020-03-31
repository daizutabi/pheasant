import pytest


@pytest.fixture()
def convert(script):
    def func(source):
        return script.convert(source, max_line_length=0)

    return func


def test_python_parse_source(convert):
    assert convert("# # Title\n") == "# Title\n"
    assert convert("# # Title\n# ## Section\n") == "# Title\n## Section\n"
    assert convert("# # Title\n\n# ## Section\n") == "# Title\n\n## Section\n"
    assert convert("# # Title\n\n# abc\n# def\n# ghi\n") == "# Title\n\nabc def ghi\n"
    assert convert("# あ\n# い\n# う\n") == "あいう\n"
    assert convert("# あa\n# い\n# う\n") == "あaいう\n"
    assert convert("# あa\n# bい\n# う\n") == "あa bいう\n"


def test_python_parse_code(convert):
    assert convert("# # Title\na=1\n") == "```python\n# # Title\na=1\n```\n"
    assert convert("# # Title\n\na=1\n") == "# Title\n\n```python\na=1\n```\n"
    assert convert("# a\na=1\n") == "```python\n# a\na=1\n```\n"


def test_python_parse_code_escaped(convert):
    assert (
        convert("# a\n# ~~~\n# abc\n# ~~~\n\na=1\n")
        == "a\n~~~\nabc\n~~~\n\n```python\na=1\n```\n"
    )

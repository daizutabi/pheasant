import pytest


@pytest.fixture()
def parse(parser):
    def func(source):
        return "".join(parser.parse(source))

    return func


def test_python_parse_source(parse):
    assert parse("# # Title\n") == "# Title\n"
    assert parse("# # Title\n\n# ## Section\n") == "# Title\n\n## Section\n"
    assert parse("# # Title\n\n# abc\n# def\n# ghi\n") == "# Title\n\nabc def ghi\n"
    assert parse("# あ\n# い\n# う\n") == "あいう\n"
    assert parse("# あa\n# い\n# う\n") == "あa いう\n"
    assert parse("# あa\n# bい\n# う\n") == "あa bいう\n"


def test_python_parse_code(parse):
    assert parse("# # Title\na=1\n") == "# Title\n```python\na=1\n```\n"
    assert parse("# # Title\n\na=1\n") == "# Title\n```python\na=1\n```\n"
    assert parse("# a\na=1\n") == "a\n```python\na=1\n```\n"


def test_python_parse_code_escaped(parse):
    print(parse("# a\n# ~~~\n# abc\n# ~~~\na=1\n"))
    assert (
        parse("# a\n# ~~~\n# abc\n# ~~~\na=1\n")
        == "a\n~~~\nabc\n~~~\n```python\na=1\n```\n"
    )

import pytest


@pytest.fixture()
def parse(parser):
    def func(source):
        return parser.parse(source)

    return func


def test_python_parse_source(parse):
    assert parse("# # Title\n") == "# Title\n\n"
    assert parse("# # Title\n# ## Section\n") == "# Title\n## Section\n\n"
    assert parse("# # Title\n\n# ## Section\n") == "# Title\n\n## Section\n\n"
    assert parse("# # Title\n\n# abc\n# def\n# ghi\n") == "# Title\n\nabc def ghi\n\n"
    assert parse("# あ\n# い\n# う\n") == "あいう\n\n"
    assert parse("# あa\n# い\n# う\n") == "あa いう\n\n"
    assert parse("# あa\n# bい\n# う\n") == "あa bいう\n\n"


def test_python_parse_code(parse):
    assert parse("# # Title\na=1\n") == "# Title\n\n```python\na=1\n```\n\n"
    assert parse("# # Title\n\na=1\n") == "# Title\n\n```python\na=1\n```\n\n"
    assert parse("# a\na=1\n") == "a\n\n```python\na=1\n```\n\n"


def test_python_parse_code_escaped(parse):
    assert (
        parse("# a\n# ~~~\n# abc\n# ~~~\na=1\n")
        == "a\n\n~~~\nabc\n~~~\n\n```python\na=1\n```\n\n"
    )

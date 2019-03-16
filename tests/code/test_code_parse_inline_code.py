import pytest


def inline_code(header, language, source):
    return f"{header}![{language}]({source})\n"


@pytest.fixture()
def parse(parser):
    def func(header, language, source, pre="", post=""):
        return "".join(
            parser.parse(pre + "\n" + inline_code(header, language, source) + post)
        )

    return func


def test_code_parse_file(tmpdir):
    p = tmpdir.join("hello.py")
    source = "def func(x):\n    return 2 * x\n\nprint(f(3))\n"
    p.write(source)
    assert p.read() == source

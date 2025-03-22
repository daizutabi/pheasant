import pytest

from pheasant.renderers.script.splitter import split


def test_split_docstring():
    source = '# test\na=1\n"""\ndocstring 1\n\ndocstring 2\n  """\na\n'
    splitter = split(source)
    assert next(splitter) == ("Code", "# test\na=1\n")
    assert next(splitter) == ("Docstring", '"""\ndocstring 1\n\ndocstring 2\n  """\n')
    assert next(splitter) == ("Code", "a\n")


@pytest.mark.parametrize("nl", ["\n", ""])
def test_parse_docstring(script, nl):
    source = f'"""\ndoc string\ndoc string\n\ntext{nl}"""\n'
    output = script.convert(source, 0)
    answer = "\n".join(
        [
            '\n<div class="pheasant-fenced-code"><div class="docstring">'
            '<pre><code class="text">doc string\ndoc string\n',
            "text</code></pre></div></div>\n\n",
        ]
    )
    assert output == answer
    output = script.convert(source, 80)
    assert output == source

    source = f'# a\n"""markdown\ndoc string\ndoc string\n\ntext{nl}"""\n# b\n'
    output = script.convert(source, 0)
    assert output == "a\n\ndoc string doc string\n\ntext\n\nb\n"
    output = script.convert(source, 80)
    answer = '# a\n"""markdown\ndoc string doc string\n\ntext\n"""\n# b\n'
    assert output == answer

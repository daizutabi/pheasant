import pytest

from pheasant.jupyter.converter import initialize, convert
from pheasant.utils import read


@pytest.fixture
def stream_input():
    return read(__file__, "mkdocs/docs/markdown_stream_input.md")


@pytest.fixture
def stream_output():
    return read(__file__, "mkdocs/docs/markdown_stream_output.md")


def test_execute_and_export_stream(stream_input, stream_output):
    initialize()
    output = convert(stream_input)
    assert isinstance(output, str)
    lines = zip(output.split("\n"), stream_output.split("\n"))
    for markdown_line, stream_output_line in lines:
        pass
        # assert markdown_line == stream_output_line

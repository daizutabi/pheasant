import pytest

from pheasant.core.parser import Parser
from pheasant.python.renderer import Python


@pytest.fixture()
def python():
    python = Python()
    return python


@pytest.fixture()
def parser(python):
    parser = Parser()

    for pattern, render in python.renders.items():
        parser.register(pattern, render)

    return parser


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "# # Title\n# ## Section a\n# paragraph 11\n# paragraph 12",
            "# paragraph 13\n\n# paragraph 21\n# paragraph 22\n# paragraph 23\n"
            "a=1\nb=2\nc=3\n# ## section b\nd=4\ne=5\nf=6\n",
        ]
    )
    return source_simple

# # Title
# ## Section
# ### Subsection

# paragraph
# paragraph

# #Fig
# ~~~
# d
# ~~~

import pytest

from pheasant.core.parser import Parser
from pheasant.script.renderer import Script


@pytest.fixture()
def source():
    with open(__file__, "r", encoding="utf-8-sig") as file:
        return file.read()

# -
@pytest.fixture()
def script():
    """
    Return a Script instance.
    """
    script = Script()
    return script

# paragaraph
# paragaraph


@pytest.fixture()
def parser(script):
    parser = Parser()

    for pattern, render in script.renders.items():
        parser.register(pattern, render)

    return parser

# paragaraph
# paragaraph

# paragaraph
# paragaraph

# -
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

# # Standalone Script

# Using Atom's [Hydorgen](https://nteract.gitbooks.io/hydrogen/) package, you can
# execute any part of Python script code in Atom editor. So you can edit your Markdown
# verifying its execution and outputs. But unfortunately, the entire Markdown source
# cannot be executed all at once as a standalone program and cannot be ran by Python
# interpreter. Pheasant connects between a pure Python script and a Markdown source for
# MkDocs. Actually, this page is written by a pure Python code.

# A basic idea is that Markdown cells and code cells generally appear alternately. We
# can write a Markdown cell with a successive comment lines. In order to be recognized
# as a Markdown cell, `#` must be at the begining of lines. But we can insert a blank
# line in a Markdown cell without `#` to make a paragraph.

# Normal Python code is treated as a code cell as you expect. If a comment is not at the
# begining of line, a code cell can contain comments.

import holoviews as hv
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from mkdocs.config import config_options  # This import required for BasePlugin
from mkdocs.plugins import BasePlugin

# Import statements are colleted at the top of module because a linter says they should
# be here.


def add(x: int, y: int) -> int:
    """Add `x` and `y`."""
    return x + y  # a comment in a code cell.


def sub(x: int, y: int) -> int:
    """Substract `y` from `x`."""
    return x - y  # a comment in a code cell.


# After code, if there is a comment started at the begining of line, it divides the
# source into a code cell and a Markdown cell. This Markdown cell will continue until
# next Python code appears.

# Despite of a Markdown cell, you may want to devide a successive code into separate
# cells. This can be done by putting a special marker between codes to tell Pheasant
# your intention. The marker is `# -` [sharp-space-minus] at the begining of lines. In
# this way you can divide the above two functions into separate cells (regardless of its
# usefullness.)


def add2(x: int, y: int) -> int:
    """Add `x` and `y`."""
    return x + y  # a comment in a code cell.


# -
def sub2(x: int, y: int) -> int:
    """Substract `y` from `x`."""
    return x - y  # a comment in a code cell.


# ## Plot libraries


plt.plot([1, 2, 3])
plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 3, 0, 2, 4], size=10)

# {{!plot}}


curve = hv.Curve(((1, 2), (3, 4)))

# {{!curve}}


# ## Internal mechanism

# By defaults, MkDocs processes Markdown files only for pages. This setting are defined
# in the MkDocs's utility library: `mkdocs.utils.markdown_extensions`. Pheasant plugin
# updates this setting in the Plugin's `on_config` event function:


class PheasantPlugin(BasePlugin):
    def on_config(self, config):
        from mkdocs.utils import markdown_extensions

        markdown_extensions.append(".py")


# By this setting, MkDocs reads a '.py' file as a Markdown source. Then, Pheasant
# converts it into a real Markdown formant in order to be processess by other converters
# later.


# ## Comment writing

# In this scheme, we have to write many comments as Markdown cells. But a linter such as
# pycodestyle doesn't allow us to write a very long comment in one line longer than (for
# example) 79 characters. This means that we have to write 'Markdown source' with
# several 'New Line' characters even we are writing 'one' paragraph. In order to
# overcome this incovenient situation, a comment wrapping pakage
# [`pyls-cwrap`](https://github.com/daizutabi/pyls-cwrap) was prepared. You can install
# this package as `pip install pyls-cwrap`. In Atom, if you use
# [`ide-python`](https://atom.io/packages/ide-python), just press [Ctrl]+[Shift]+[C]
# (Windows, default setting), sequential comments are automatically formatted.

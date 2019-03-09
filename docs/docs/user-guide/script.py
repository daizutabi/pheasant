# # Standalone Script

# Using Atom's [Hydorgen](https://nteract.gitbooks.io/hydrogen/) package, you can
# execute any Python script codes in a Markdown source. So you can edit your Markdown
# verifying its execution and outputs. But unfortunately (as long as I know), the entire
# Markdown source cannot be executed all at once as a standalone script and cannot be
# ran by Python interpreter. Pheasant connects between a pure Python script and a
# Markdown source for MkDocs. Actually, this page is written by a pure Python code.

# ## How to

# A basic idea is that Markdown cells and code cells generally appear alternately. We
# can write a Markdown cell with a successive comment lines. In order to be recognized
# as a Markdown cell, `#` must be at the begining of lines. But we can insert a blank
# line in a Markdown cell without `#` to make a paragraph.

# Normal Python code is treated as a code cell as you expect. If a comment is not at the
# begining of line, a code cell can contain comments.


def add(x: int, y: int) -> int:
    """Add `x` and `y`."""
    return x + y  # a comment in a code cell.


def sub(x: int, y: int) -> int:
    """Substract `y` from `x`."""
    return x - y  # a comment in a code cell.


# When a comment starts at the begining of a line after a code block, it divides the
# source into a code cell and a Markdown cell. This Markdown cell will continue until
# next Python code appears.

# Despite of a Markdown cell, you may want to devide successive codes into separate
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


# ## Internal mechanism

# By defaults, MkDocs processes Markdown files only for pages. This setting is defined
# in the MkDocs's utility library: `mkdocs.utils.markdown_extensions`. Pheasant plugin
# updates this setting in the Plugin's `on_config` event function:


from mkdocs.config import config_options  # This import required for BasePlugin
from mkdocs.plugins import BasePlugin


class PheasantPlugin(BasePlugin):
    def on_config(self, config):
        from mkdocs.utils import markdown_extensions

        markdown_extensions.append(".py")


# By this setting, MkDocs reads a ".py" file as a Markdown source. Then, Pheasant will
# convert it into a real Markdown format in order to be processed by other converters
# later.


# ## Comment writing

# In this scheme, we have to write many comments for Markdown cells. But a linter such
# as pycodestyle doesn't allow us to write a very long comment in one line longer than
# (for example) 79 characters. This means that we have to write 'Markdown source' with
# several 'New Line' characters even we are writing 'one' paragraph. In order to
# overcome this incovenient situation, a comment wrapping pakage
# [`pyls-cwrap`](https://github.com/daizutabi/pyls-cwrap) was prepared. You can install
# this package as `pip install pyls-cwrap`. In Atom, if you use
# [`ide-python`](https://atom.io/packages/ide-python), just press [Ctrl]+[Shift]+[C]
# (Windows, default setting), sequential comments are automatically formatted.

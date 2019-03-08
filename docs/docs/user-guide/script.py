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
# this way you can divide the above two functions into separate cell (regardless of its
# usefullness.)


def add2(x: int, y: int) -> int:
    """Add `x` and `y`."""
    return x + y  # a comment in a code cell.


# -
def sub2(x: int, y: int) -> int:
    """Substract `y` from `x`."""
    return x - y  # a comment in a code cell.


# (continued)

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

# Python code block is treated as a code cell as you expect. Code cells can contain any
# comments as long as the comments don't start at the begining of line.


def add(x: int, y: int) -> int:
    """Add `x` and `y`."""
    return x + y  # a comment in a code cell.


def sub(x: int, y: int) -> int:
    """Substract `y` from `x`."""
    return x - y  # a comment in a code cell.


# When a comment starts at the begining of line after a code block, it divides the
# source into a code cell and a Markdown cell. This Markdown cell will continue until
# next Python code appears.

# Despite of a Markdown cell, you may want to devide successive codes into separate
# cells. This can be done by putting a special marker between codes to tell Pheasant
# your intention. The marker is `# -` [sharp-space-minus] at the begining of line. For
# example,

# ~~~python
# a, b = 1, 2
# a
# # -
# b
# ~~~

# becomes:

a, b = 1, 2
a
# -
b

# You can add options to a code block by adding them after a block devider (`# -`).

# ~~~python
# # -hide
# c = 3
# # Output: `c` is equal to {{c}}.
# ~~~

# Above python code is equivalent to the next Markdown source.
# ~~~
# ```python hide
# c = 3
# ```
# Output: `c` is equal to {{c}}.
# ~~~

# -hide
c = 3
# Output: `c` is equal to {{c}}.

# Other Pheasant features also work. For example, go to Fig. {#cat#}

# ## Fenced code block in Python source
# You can write a fenced code block in a Python source as comment.

# ~~~python
# # ```python
# # print(1)
# # ```
# ~~~

# becomes:

# ```python
# print(1)
# ```

# And,

# ~~~python
# # ~~~
# # ```python
# # print(1)
# # ```
# # ~~~
# ~~~


# becomes:

# ~~~
# ```python
# print(1)
# ```
# ~~~

# ## Comment writing package
# In this scheme, we have to write many comments for Markdown cells. But a linter such
# as pycodestyle doesn't allow us to write a very long comment in one line longer than
# (for example) 79 characters. This means that we have to write 'Markdown source' with
# several 'New Line' characters even we are writing 'one' paragraph. In order to
# overcome this incovenient situation, a comment wrapping pakage
# [`pyls-cwrap`](https://github.com/daizutabi/pyls-cwrap) has been prepared. You can
# install this package as `pip install pyls-cwrap`. In Atom, if you use
# [`ide-python`](https://atom.io/packages/ide-python), just press [Ctrl]+[Shift]+[C]
# (Windows, default setting), sequential comments are automatically formatted.

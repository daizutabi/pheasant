# # Standalone Script
# Using Atom's [Hydrogen](https://nteract.gitbooks.io/hydrogen/) package, you can
# execute any Python script codes within a fenced code block in a Markdown source. So
# you can edit your code verifying its execution results. But unfortunately (as long as
# I know), the entire Markdown source cannot be executed all at once as a standalone
# script and cannot be ran by Python interpreter. Pheasant connects between a pure
# Python script and a Markdown source. Actually, this page is written by a pure Python
# code.
# ## How to
# A basic idea is that Markdown cells and Python code cells generally appear
# alternately. We can write a Markdown cell with a successive comment lines. In order to
# be recognized as a Markdown cell, `#` must be at the begining of lines. But we can
# insert a blank line to make a paragraph.

# Normal Python code is treated as a code cell as you expect.


def add(x: int, y: int) -> int:
    """Add `x` and `y`."""
    return x + y


def sub(x: int, y: int) -> int:
    """Substract `y` from `x`."""
    return x - y


# When a comment starts at the begining of line after a code block, it divides the
# source into a code cell and a Markdown cell. This new Markdown cell will continue
# until next Python code appears.

# If you want to include a comment at the begining of line, you can write the comment
# just above the following codes without a blank line.

# ~~~python
# # First comment in a code cell.
# a = 2
# ~~~

# becomes

# First comment in a code cell.
a = 2

# Despite of a Markdown cell, you may want to devide successive codes into separate
# cells. This can be done by putting a special inline comment to define a cell. The
# comment pattern is `# -`. For example,

# ~~~python
# a, b, c = 1, 2, 3
# a
# # -
# b
# ~~~

# becomes

a, b, c = 1, 2, 3
a
# -
b

# You can add options to a code block by adding them after a cell devider.

# ~~~python
# # -hide
# d = 4
# # * Output: `d` is equal to {{d}}.
# ~~~

# Above python code is equivalent to the next Markdown source.

# ~~~
# ```python hide
# d = 4
# ```
# * Output: `d` is equal to {{d}}.
# ~~~

# Then you can hide the python code cell.

# -hide
d = 4
# * Output: `d` is equal to {{d}}.

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

# ## A package for comment formatting
# In this scheme, we have to write many comments for Markdown cells. But a linter such
# as pycodestyle doesn't allow us to write a very long comment in one line longer than
# (for example) 79 characters. This means that we have to write Markdown source with
# several new line characters even we are writing one paragraph. In order to overcome
# this incovenient situation, a comment formatting pakage
# [`pyls-cwrap`](https://github.com/daizutabi/pyls-cwrap) has been prepared. You can
# install this package as `pip install pyls-cwrap`. In Atom, if you use
# [`ide-python`](https://atom.io/packages/ide-python), just press [Ctrl]+[Shift]+[C]
# (Windows, default setting), sequential comments are automatically formatted nicely.

# ## Source code
# #File script.py {%=script.py%}

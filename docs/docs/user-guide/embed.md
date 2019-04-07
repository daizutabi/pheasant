# Embeded objects

Pheasant can embed codes from a file system or Python module.

## File system

Extenal resources are read from file system by Pheasant syntax: `{%# =object %}`. For example,

~~~
{%=/mkdocs.yml%}
~~~

writes the content of the real `mkdocs.yml` of this document:

{%=/mkdocs.yml%}

The root directory is the directory where `mkdocs.yml` exists.

If the file is too long to display the whole content, you can specify the lines as the same way that Python does with the slice notation.

~~~copy
{%=/mkdocs.yml[3:8]%}
~~~

Imported file can be numbered like figures and tables. Use this inline notation:

~~~copy
#File 1.2 {%=/mkdocs.yml[:8]%}
~~~

## Python module source

Python module sources that the current Jupyter kernel can find are also inspected. Now Pheasant imported its own package `pheasant`, so you can read the source from this document.

You can write to inspect the whole module content:

~~~copy
{%?pheasant%}
~~~

A part of the module can be specified as usual.

```python
from pheasant.renderers.jupyter.jupyter import Jupyter
```

~~~copy
{%?Jupyter[:23]%}
~~~

With this functionality, you can guarantee the reproducible relation between your source code and results easily.

## Include other file as Markdown source.

Assume that there is a directory named `link` under the same directory of this file and there are some files under the `link` directory. You can include the content of a file like below:

~~~copy
{% link/included.md %}
~~~

You can also include a pure Python source code.

~~~copy
{% link/included.py %}
~~~

If the included file contains header statements, the document structure may be broken. For example, a file to be included contains:

#File <code>link/section.md</code> {% =link/section.md %}

If you include the file, a new `<h1>` section starts that you don't want to. To maintain the document structure, you can shift the header level like below. Note that we are under a `<h2>` section now.

~~~
{% link/section.md>2 %}
~~~

In this case, "`# Title`" becomes "`### Title`" by "`>2`".

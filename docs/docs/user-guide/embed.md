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

~~~copy
{% link/included.md %}
~~~

~~~copy
{% link/included.py %}
~~~

If the included file contains header statement, the documents structure may be broken. For example, an included file contains:

#File <code>link/section.md</code> includes section headers. {% =link/section.md %}

Then,

~~~copy
{% link/section.md %}
~~~

Here, a new `<h1>` section starts. To maintain the document structure, you can shift the header level like this.

You can shift the level of headers like below:

~~~copy
{% link/section.md>2 %}
~~~

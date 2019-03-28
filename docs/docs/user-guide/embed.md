# Embeded objects

Pheasant can embed codes from a file system or Python module.

## File system

Extenal resources are read from file system by Pheasant syntax: `{%#object%}`. For example,

~~~
{%mkdocs.yml%}
~~~

writes the content of the real `mkdocs.yml` of this document:

{% mkdocs.yml %}

The root directory is the directory where `mkdocs.yml` exists.

If the file is too long to display the whole content, you can specify the lines as the same way that Python does with the slice notation.

~~~copy
{%mkdocs.yml[3:8]%}
~~~

Imported file can be numbered like figures and tables. Use this inline notation:

~~~copy
#file {%mkdocs.yml[:8]%}
~~~

## Python module source

Python module sources that the current Jupyter kernel can find are also inspected. Now Pheasant imported its own package `pheasant`, so you can read the source from this document.

You can write to inspect the whole module content:

~~~copy
{%?pheasant%}
~~~

A part of the module can be specified as usual.

```python
from pheasant.jupyter.renderer import Jupyter
```

~~~copy
{%?Jupyter[:23]%}
~~~

With this functionality, you can guarantee the reproducible relation between your source code and results easily.

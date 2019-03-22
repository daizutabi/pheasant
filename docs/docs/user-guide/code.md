# Inspect and Load Codes

Pheasant can read codes from a file system or Python module.

## File system

Any text files are read from file system by Pheasant's extended Markdown syntax: `![file](<file name>)`. For example,

~~~
![file](mkdocs.yml)
~~~

writes the content of the real `mkdocs.yml` of this document:

![file](mkdocs.yml)

The root directory of a relative path is the directory where `mkdocs.yml` exists.

If the file is too long to display the whole content, you can specify the lines as the same way that Python does with the slice notation. Use `<` and `>` insted of `[` and `]` because `[` and `]` can be a part of a file name.

~~~copy
![file](mkdocs.yml<5:10>)
~~~

Imported file can be numbered like figures and tables. Use this shorthand notation:

~~~copy
#![file](mkdocs.yml<:8>)
~~~

## Python module source

Python module sources that the current Jupyter kernel can find are also inspected. Now Pheasant imported its own package `pheasant`, so you can read the source from this document.

You can write to inspect the whole module content:

~~~copy
#![python](pheasant)
~~~

Just version number now.

A part of the module can be specified as usual.

```python
from pheasant.core import page
```

~~~copy
#![python](page.Page)
~~~

With this functionality, you can guarantee the reproducible relation between your source code and results easily.

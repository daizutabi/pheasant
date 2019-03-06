# Code

Pheasant can include codes from Python moudle or a file system.

## File system

Any text files are read from file system by Pheasant's extended Markdown syntax. For example,

~~~copy
![file](mkdocs.yml)
~~~

The root directory of a relative path is the directory where `mkdocs.yml` exists.

If the file is too long to display the whole content, you can specify the lines as the same way Python does with the slice notation. Use `<` and `>` insted of `[` and `]` because `[` and `]` can be a part of a file name.

~~~copy
![file](mkdocs.yml<4:10>)
~~~

When you want to specify a language, write like below after `?` character:

~~~
![file](example.js<:10>?javascript)
~~~

Imported file can be numbered like figures and tables. Use this shorthand notation:

~~~copy
#![file](pheasant.yml)
~~~

The above file is the real config file of this Pheasant document.

## Python source

Python module sources that the current Jupyter kernel can find are also inspected. Now Pheasant is configured like the above `phesant.yml` settings,
the kernel's `sys.path` includes `scripts` directory and module `example` has already imported.

```python
import sys
sys.path[:5]
```

```python
example
```

You can write to inspect the whole module content:

~~~copy
#![python](example)
~~~

A part of the module can be specified as usual.

~~~copy
#![python](example.sub)
~~~

With this functionality, you can guarantee the reproducible relation between your source code and results easily.

# Code

Pheasant can include codes from Python moudle or a file system.

## File

Any text files are read from file system by Pheasant's extended Markdown syntax. For example,

~~~copy
![file](mkdocs.yml)
~~~

The root directory of a relative path is the directory where `mkdocs.yml` exists.

If the file is too long to display the whole content, you can specify the lines to show as the same way Python does with the slice notation by `<` and `>` insted of `[` and `]`.

~~~copy
![file](mkdocs.yml<4:10>)
~~~

When you specify the language, write like below:

~~~
![file](example.js<:10>?javascript)
~~~

Imported file can be numbered like figures and tables. Use this shorthand notation:

~~~copy
#![file](pheasant.yml)
~~~

The above file is the real config file of this Pheasant document.

## Python module source

Python module sources that the current Jupyter kernel can find are also inspected. Now Pheasant is configured like the above `phesant.yml` setting,
the kernel's `sys.path` includes `scripts` directory and module `example` has already imported.

```python
import sys
sys.path[:5]
```


#Code d
![python](example)

#![python](example)

# ##Release Notes

---

## Upgrading

To upgrade Pheasant to the latest version, use pip:

~~~
pip install -U pheasant
~~~

You can determine your currently installed version using `pheasant --version`:

~~~
$ pheasant --version
pheasant, version 2.0.1 from /path/to/pheasant (Python 3.7)
~~~

## Change log

### Version 2.0.1 (2019-03-26)

* Scritpt converter: docstring bug fix.

### Version 2.0.0 (2019-03-26)

* Drop Python 3.6 support in favor of Python 3.7 dataclass.
* Macro converter: deleted.

### Version 1.2.2 (2019-03-10)

* Macro converter: inline code enabled powered by Jupyter converter.

### Version 1.2.1 (2019-03-10)

* Script converter: bug fix for escape code.

### Version 1.2.0 (2019-03-10)

* New **Script** converter for pure Python code ('.py').

### Version 1.1.0 (2019-03-07)

* [Black](https://github.com/ambv/black) formatted.
* Drop dependency on [nbconvert](https://nbconvert.readthedocs.io/en/latest/) and [nbformat](https://nbformat.readthedocs.io/en/latest/). Code is executed as a plain source instead of a Jupyter Notebook's cell.
* Kernel client's `execute_interactive` method invoked instead of `execute` method. The method is new in Version 5.0 of [jupyter_client](https://jupyter-client.readthedocs.io/en/stable/index.html).

### Version 1.0.0 (2019-03-05)

* First major release.

# ##Release Notes

---

## Upgrading

To upgrade Pheasant to the latest version, use pip:

~~~bash terminal
$ pip install -U pheasant
~~~

You can check your currently installed version using `pheasant --version`:

~~~bash terminal
$ pheasant --version
pheasant, version 2.2.33 from /path/to/pheasant (Python 3.7)
~~~

## Change log

### Version 2.4.2 (2020-03-11)

* Current directory (`os.curdir`) of Python jupyter kernel is automatically changed to the directory in which the current page exists.

### Version 2.4.1 (2020-03-11)

* To disable numbering, in mkdocs.yaml:

~~~yaml
plugins:
  - pheasant:
      header:
        disabled: true
~~~

### Version 2.4.0 (2020-03-08)

* Support for MkDocs 1.1

### Version 2.2.33 (2019-05-26)

* Configurable link like `{## tag | Ch 1 Sec 2 #}`

### Version 2.2.32 (2019-05-14)

* `freeze` option to keep the cache.

### Version 2.2.31 (2019-05-11)

* `inspect` option to get source.
* Bug fixed: Update cache for code with an unknown kernel name.

### Version 2.2.30 (2019-05-10)

* jupyter.kernel: raises `NameError` to delete cache and rerun.

### Version 2.2.29 (2019-05-09)

* Bug fixed: `utils.latex`

### Version 2.2.28 (2019-05-09)

* Script renderer: `# %%`-type inline comment to define a code cell.

### Version 2.2.27 (2019-05-07)

* `dirty` mode in Converter for MkDocs serve command.

### Version 2.2.25 (2019-05-06)

* Display support for jpeg and gif.

### Version 2.2.24 (2019-05-05)

* `pheasant.utils.latex` module to create LaTeX strings.

### Version 2.2.22 (2019-05-02)

* Build documentation without `nav`.

### Version 2.2.21 (2019-04-29)

* Add version config for pheasant plugin.

### Version 2.2.20 (2019-04-26)

* Print text output from Jupyter Kernel in verbose mode.

### Version 2.2.19 (2019-04-23)

* Use IPython formatter to display rich data.

### Version 2.2.18 (2019-04-21)

* CLI: `pheasant run --restart` command to restart kernel.
* CLI: `pheasant run --force` command to delete cache.

### Version 2.2.17 (2019-04-21)

* CLI: `pheasant clean` command accepts normal source args.

### Version 2.2.16 (2019-04-20)

* Remove cache if mismatch occurs in safe mode.

### Version 2.2.15 (2019-04-17)

* New progress bar with multi-step.
* Cache system reconstructed.

### Version 2.2.14 (2019-04-16)

* `pheasant --clear` -> `pheasant clean`.
* New progress bar

### Version 2.2.13 (2019-04-15)

* Delete cache: `pheasant --clear`.

### Version 2.2.12 (2019-04-15)

* Cache on jupyter renderer.

### Version 2.2.11 (2019-04-15)

* Cache includes page toc.

### Version 2.2.10 (2019-04-15)

* External link from section headers.

### Version 2.2.9 (2019-04-15)

* Delete jQuery tooltip for stability.

### Version 2.2.8 (2019-04-13)

* Allow directory in nav entry for automatic page collection.

### Version 2.2.7 (2019-04-12)

* PheasantPlugin: introduce cache system.

### Version 2.2.6 (2019-04-11)

* Script render: bug fix for list notations.

### Version 2.2.5 (2019-04-10)

* Custom theme for documentation.
* Retry kernel start when timeout.

### Version 2.2.4 (2019-04-10)

* Prompt icons.

### Version 2.2.3 (2019-04-09)

* termcolor.

### Version 2.2.2 (2019-04-09)

* CSS/JS update.

### Version 2.2.0 (2019-04-09)

* Rewrite MANIFEST.in, setup.py

### Version 2.1.6 (2019-04-08)

* Add progress bar for jupyter converter.

### Version 2.1.5 (2019-04-07)

* Add pheasant.js for show/hide source.

### Version 2.1.4 (2019-04-07)

* Add link to extra_css and extra_javascript (theme/pheasant.yml)

### Version 2.1.3 (2019-04-06)

* Multi-line header for python script. `# # a\n# # b\n` -> `# # a b\n`

### Version 2.1.2 (2019-04-06)

* Bug fix: Altair plot with a True option (True -> true)

### Version 2.1.1 (2019-04-05)

* Header: reset numbering with a '!' character. `# !Title\n` or just `#!\n`.

### Version 2.1.0 (2019-04-04)

* Add feature to import extra pages.
* Jupyter: multi-stdout/err into a joined cell.

### Version 2.0.13 (2019-04-04)

* Page selection if page titles end with `*` (MkDocs Plugin).

### Version 2.0.11 (2019-04-03)

* Skip files not in nav (MkDocs Plugin).

### Version 2.0.10 (2019-04-02)

* SymPy and numbered equation supported.

### Version 2.0.4 (2019-03-28)

* Altair plot can be embeded.

### Version 2.0.3 (2019-03-27)

* New Embed converter replacing Code converter.

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

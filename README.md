[![PyPI version][pypi-image]][pypi-link]
[![Python versions][pyversions-image]][pyversions-link]
[![Travis][travis-image]][travis-link]
[![AppVeyor][appveyor-image]][appveyor-link]
[![Coverage Status][coveralls-image]][coveralls-link]
[![Code style: black][black-image]][black-link]

[pypi-image]: https://badge.fury.io/py/pheasant.svg
[pypi-link]: https://pypi.org/project/pheasant
[travis-image]: https://travis-ci.org/daizutabi/pheasant.svg?branch=master
[travis-link]: https://travis-ci.org/daizutabi/pheasant
[appveyor-image]: https://ci.appveyor.com/api/projects/status/ys2ic8n4j7r5j4bg/branch/master?svg=true
[appveyor-link]: https://ci.appveyor.com/project/daizutabi/pheasant
[coveralls-image]: https://coveralls.io/repos/github/daizutabi/pheasant/badge.svg?branch=master
[coveralls-link]: https://coveralls.io/github/daizutabi/pheasant?branch=master
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
[pyversions-image]: https://img.shields.io/pypi/pyversions/pheasant.svg
[pyversions-link]: https://pypi.org/project/pheasant

<!--
[![Anaconda Version][anaconda-v-image]][anaconda-v-link]
[anaconda-v-image]: https://anaconda.org/daizutabi/pheasant/badges/version.svg
[anaconda-v-link]: https://anaconda.org/daizutabi/pheasant
-->

# Pheasant

Pheasant is a Markdown converter which is designed to be used as a plugin for static site generators, especially MkDocs. The one of the main features of Pheasant is auto Markdown generation of outputs after execution of any Python or other language codes written in a fenced code block of Markdown source. This process is executed by the Jupyter client functionality. In addition to the code execution, Pheasant can automatically number headers, figures, tables, *etcs*.

## Setup

Install the plugin using pip:

```bash
pip install pheasant
```

Next, add the following lines to your `mkdocs.yml`:

```yml
plugins:
  - search
  - pheasant
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

## Documentation

See [Pheasant documentation](https://pheasant.daizutabi.net).

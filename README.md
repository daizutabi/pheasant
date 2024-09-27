# Pheasant

[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Python Version][python-v-image]][python-v-link]
[![Build Status][GHAction-image]][GHAction-link]
[![Coverage Status][codecov-image]][codecov-link]


Pheasant is a Markdown converter which is designed to be used as a plugin
for static site generators, especially MkDocs. The one of the main features
of Pheasant is auto Markdown generation of outputs after execution of any
Python or other language codes written in a fenced code block of Markdown source.
This process is executed by the Jupyter client functionality.

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


<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/pheasant.svg
[pypi-v-link]: https://pypi.org/project/pheasant/
[python-v-image]: https://img.shields.io/pypi/pyversions/pheasant.svg
[python-v-link]: https://pypi.org/project/pheasant
[GHAction-image]: https://github.com/daizutabi/pheasant/actions/workflows/ci.yml/badge.svg?branch=main&event=push
[GHAction-link]: https://github.com/daizutabi/pheasant/actions?query=event%3Apush+branch%3Amain
[codecov-image]: https://codecov.io/github/daizutabi/pheasant/coverage.svg?branch=main
[codecov-link]: https://codecov.io/github/daizutabi/pheasant?branch=main

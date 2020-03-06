import os
import re
import subprocess
import sys

from setuptools import setup


def get_version(package: str) -> str:
    """Return version of the package."""
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), package, "__init__.py"
    )
    with open(path, "r") as file:
        source = file.read()
    m = re.search(r'__version__ = ["\'](.+)["\']', source)
    if m:
        return m.group(1)
    else:
        return "0.0.0"


def get_packages(package):
    """Return root package and all sub-packages."""
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


long_description = (
    "Pheasant is a Markdown converter which is designed to be used "
    "as a plugin for static site generators, especially MkDocs. "
    "The Pheasant main feature is auto generation of outputs for a fenced "
    "code block in Markdown source using Jupyter client. In addition, "
    "Pheasant can automatically number headers, figures, tables, etc."
)


def check():
    def run(command):
        assert subprocess.run(command.split()).returncode == 0
        print(f"'{command}' --- OK")

    run("pycodestyle pheasant")
    run("pyflakes pheasant")
    run("mypy pheasant")
    run("pycodestyle tests")
    run("pyflakes tests")


def publish():
    check()
    subprocess.run("python setup.py sdist bdist_wheel".split())
    subprocess.run("twine upload dist/*".split())
    version = get_version("pheasant")
    subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"'Version {version}'"])
    subprocess.run(["git", "push", "origin", "--tags"])
    sys.exit(0)


if sys.argv[-1] == "publish":
    publish()

if sys.argv[-1] == "check":
    check()

setup(
    name="pheasant",
    version=get_version("pheasant"),
    description="Documentation tool for Markdown conversion by Jupyter client.",
    long_description=long_description,
    url="https://pheasant.daizutabi.net",
    author="daizutabi",
    author_email="daizutabi@gmail.com",
    license="MIT",
    packages=get_packages("pheasant"),
    include_package_data=True,
    install_requires=[
        "click",
        "ipykernel",
        "markdown",
        "jinja2",
        "termcolor",
        "colorama",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["pheasant = pheasant.main:cli"],
        "mkdocs.plugins": ["pheasant = pheasant.plugins.mkdocs:PheasantPlugin"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Documentation",
    ],
)

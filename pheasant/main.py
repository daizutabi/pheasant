import os
import shutil
import sys

import click
from markdown import Markdown

from pheasant import __version__
from pheasant.core.pheasant import Pheasant

pgk_dir = os.path.dirname(os.path.abspath(__file__))
version_msg = f"{__version__} from {pgk_dir} (Python {sys.version[:3]})."


@click.command()
@click.version_option(version_msg, "-V", "--version")
@click.option("--clear", is_flag=True, help="Delete cache under the current directory.")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation.")
@click.argument("path", nargs=-1, type=click.Path(exists=True))
def cli(path, clear, yes):
    if clear:
        clear_cache(yes)
        return

    if not path:
        prompt()
    else:
        convert(path)


def convert(paths):
    pheasant = Pheasant()
    outputs = pheasant.convert_from_files(paths)
    markdown = Markdown()

    htmls = []
    for output in outputs:
        html = markdown.convert(output).strip()
        htmls.append(html)
    html = "\n".join(htmls)
    click.echo(html)


def prompt():
    lines = []
    while True:
        line = click.prompt("", type=str, default="", show_default=False)
        if lines and lines[-1] == "" and line == "":
            break
        lines.append(line)
    source = "\n".join(lines) + "\n"

    pheasant = Pheasant()
    output = pheasant.convert(source, ["main", "link"])
    click.echo("---[Markdown]---")
    click.echo(output[:-1], nl=False)
    click.echo("---[HTML]-------")
    markdown = Markdown()
    html = markdown.convert(output).strip()
    click.echo(html)
    click.echo("----------------")


def clear_cache(yes):
    for dirpath, dirnames, filenames in os.walk("."):
        if dirpath.endswith(".pheasant_cache"):
            confirm = f"Delete {len(filenames)} cache files in '{dirpath}'?"
            if yes or click.confirm(confirm):
                shutil.rmtree(dirpath)
                click.echo(f"'{dirpath}' deleted")

import logging
import os
import shutil
import sys

import click
from markdown import Markdown

from pheasant import __version__
from pheasant.core.pheasant import Pheasant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pheasant")

pgk_dir = os.path.dirname(os.path.abspath(__file__))
version_msg = f"{__version__} from {pgk_dir} (Python {sys.version[:3]})."


@click.group(
    invoke_without_command=True,
    help="If any commands are given, prompt will be invoked.",
)
@click.pass_context
@click.version_option(version_msg, "-V", "--version")
def cli(ctx):
    if ctx.invoked_subcommand is None:
        prompt()


@cli.command(help="Delete cache under the current directory recursively.")
@click.confirmation_option(prompt="Are you sure you want to delete the cache?")
def clear():
    for dirpath, dirnames, filenames in os.walk("."):
        if dirpath.endswith(".pheasant_cache"):
            shutil.rmtree(dirpath)
            click.echo(f"'{dirpath}' deleted. {len(filenames)} files.")


@cli.command(help="Run source files and save the cache.")
@click.option(
    "-e",
    "--ext",
    default="md,py",
    show_default=True,
    help="File extension(s) separated by commas.",
)
@click.option("--max", default=100, show_default=True, help="Maximum number of files.")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def run(paths, ext, max):
    ext = "." + ext.replace(",", ".")
    src_paths = []
    abs_src_paths = []

    def collect(path):
        if os.path.splitext(path)[-1] in ext:
            src_paths.append(path)
            abs_src_paths.append(os.path.abspath(path))

    if not paths:
        paths = ["."]
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    collect(os.path.join(dirpath, file))
        else:
            collect(path)
    length = len(src_paths)
    click.secho(f"collected {length} files.", bold=True)
    if length > max:
        click.echo(f"Too many files. Aborted.")

    pheasant = Pheasant()
    pheasant.convert_from_files(abs_src_paths)


def prompt():
    lines = []
    while True:
        line = click.prompt("", type=str, default="", show_default=False)
        if lines and lines[-1] == "" and line == "":
            break
        lines.append(line)
    source = "\n".join(lines).strip() + "\n"

    pheasant = Pheasant()
    output = pheasant.convert(source, ["main", "link"])
    click.echo("---[source]---")
    click.echo(source.strip())
    click.echo("---[markdown]---")
    click.echo(output.strip())
    click.echo("---[html]-------")
    markdown = Markdown()
    html = markdown.convert(output)
    click.echo(html.strip())
    click.echo("----------------")

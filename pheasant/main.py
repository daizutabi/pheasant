import os
import shutil
import sys

import click

from pheasant import __version__

pgk_dir = os.path.dirname(os.path.abspath(__file__))
version_msg = f"{__version__} from {pgk_dir} (Python {sys.version[:3]})."


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version_msg, "-V", "--version")
def cli(ctx):
    if ctx.invoked_subcommand is None:
        prompt()


@cli.command(help="Delete caches at the current directory recursively.")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation.")
def clean(yes):
    dirs = []
    for dirpath, dirnames, filenames in os.walk("."):
        if dirpath.endswith(".pheasant_cache"):
            num = len(filenames)
            files = f"{num} file"
            if num > 1:
                files += "s"
            dirpath = os.path.normpath(dirpath)
            dirs.append(dirpath)
            click.echo(f"Directory: {dirpath} ({files})")

    if not dirs:
        click.echo("No caches to delete.")
        return

    if not yes and dirs:
        click.confirm("Are you sure you want to delete the caches?", abort=True)

    for dirpath in dirs:
        shutil.rmtree(dirpath)

    click.echo("Deleted.")


ext_option = click.option(
    "-e",
    "--ext",
    default="md,py",
    show_default=True,
    help="File extension(s) separated by commas.",
)
max_option = click.option(
    "--max", default=100, show_default=True, help="Maximum number of files."
)
paths_argument = click.argument("paths", nargs=-1, type=click.Path(exists=True))


def collect(paths, ext):
    exts = ext.split(",")
    src_paths = []

    def has_cache(path):
        directory, path = os.path.split(path)
        path = os.path.join(directory, ".pheasant_cache", path + ".cache")
        return os.path.exists(path)

    def collect(path):
        if os.path.splitext(path)[-1][1:] in exts:
            cache = has_cache(path)
            src_paths.append((os.path.normpath(path), cache))

    if not paths:
        paths = ["."]
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    collect(os.path.join(dirpath, file))
        else:
            collect(path)
    return src_paths


@cli.command(help="Run source files and save the caches.")
@ext_option
@max_option
@paths_argument
def run(paths, ext, max):
    paths = collect(paths, ext)

    length = len(paths)
    click.secho(f"collected {length} files.", bold=True)

    if len(paths) > max:
        click.secho(f"Too many files. Aborted.", fg="yellow")
        sys.exit()

    from pheasant.core.pheasant import Pheasant

    pheasant = Pheasant()
    pheasant.convert_from_files(path for path, _ in paths)
    click.secho(f"{pheasant.log.info}", bold=True)


@cli.command(help="List source files.")
@ext_option
@paths_argument
def list(paths, ext):
    paths = collect(paths, ext)

    for path, cache in paths:
        if cache:
            path = "  " + path + " (cached)"
        else:
            path = "* " + path

        click.echo(path)

    length = len(paths)
    click.secho(f"collected {length} files.", bold=True)


def prompt():
    click.echo("Enter double blank lines to exit.")
    lines = []
    while True:
        line = click.prompt("", type=str, default="", show_default=False)
        if lines and lines[-1] == "" and line == "":
            break
        lines.append(line)
    source = "\n".join(lines).strip() + "\n"

    from markdown import Markdown
    from pheasant.core.pheasant import Pheasant

    pheasant = Pheasant()
    pheasant.jupyter.safe = True
    output = pheasant.parse(source, "main")
    output = pheasant.parse(output, "link")
    click.echo("[source]")
    click.echo(source.strip())
    click.echo("[markdown]")
    click.echo(output.strip())
    click.echo("[html]")
    markdown = Markdown()
    html = markdown.convert(output)
    click.echo(html.strip())

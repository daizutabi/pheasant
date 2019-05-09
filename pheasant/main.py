import os
import sys

import click

from pheasant import __version__
from pheasant.utils.cache import collect

pgk_dir = os.path.dirname(os.path.abspath(__file__))
version_msg = f"{__version__} from {pgk_dir} (Python {sys.version[:3]})."


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version_msg, "-V", "--version")
def cli(ctx):
    if ctx.invoked_subcommand is None:
        prompt()


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


@cli.command(help="Run source files and save the caches.")
@click.option("-r", "--restart", is_flag=True, help="Restart kernel after run.")
@click.option("-s", "--shutdown", is_flag=True, help="Shutdown kernel after run.")
@click.option("-f", "--force", is_flag=True, help="Delete cache and run.")
@click.option(
    "-v", "--verbose", count=True, help="Print input codes and/or outputs from kernel."
)
@ext_option
@max_option
@paths_argument
def run(paths, ext, max, restart, shutdown, force, verbose):
    caches = collect(paths, ext)

    length = len(caches)
    click.secho(f"collected {length} files.", bold=True)

    if len(caches) > max:  # pragma: no cover
        click.secho(f"Too many files. Aborted.", fg="yellow")
        sys.exit()

    if force:
        for cache in caches:
            if cache.has_cache:
                path = cache.cache_path
                os.remove(path)
                click.echo(path + " was deleted.")

    from pheasant.core.pheasant import Pheasant

    converter = Pheasant(restart=restart, shutdown=shutdown, verbose=verbose)
    converter.jupyter.safe = True
    converter.convert_from_files(cache.path for cache in caches)
    click.secho(f"{converter.log.info}", bold=True)


@cli.command(help="List source files.")
@ext_option
@paths_argument
def list(paths, ext):
    caches = collect(paths, ext)

    def size(cache):
        size = cache.size / 1024
        if size > 1024:
            size /= 1024
            return f"{size:.01f}MB"
        else:
            return f"{size:.01f}KB"

    for cache in caches:
        path = (
            ("* " if cache.modified else "  ")
            + cache.path
            + (f" (cached, {size(cache)})" if cache.has_cache else "")
        )
        click.echo(path)

    click.secho(f"collected {len(caches)} files.", bold=True)


@cli.command(help="Delete caches for source files.")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation.")
@ext_option
@paths_argument
def clean(paths, ext, yes):
    caches = [cache for cache in collect(paths, ext) if cache.has_cache]

    for cache in caches:
        click.echo(cache.path)

    length = len(caches)
    if length == 0:
        click.secho(f"No cache found. Aborted.", bold=True)
        sys.exit()

    click.secho(f"collected {length} files.", bold=True)

    if not yes:
        click.confirm(
            "Are you sure you want to delete the caches for these files?", abort=True
        )

    for cache in caches:
        path = cache.cache_path
        os.remove(path)
        click.echo(path + " was deleted.")


@cli.command(help="Python script prompt.")
def python():
    prompt(script=True)


def prompt(script=False):
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

    converter = Pheasant()
    if script:
        source = converter.parse(source, "script")
    output = converter.parse(source, "main")
    output = converter.parse(output, "link")
    click.echo("[source]")
    click.echo(source.strip())
    click.echo("[markdown]")
    click.echo(output.strip())
    click.echo("[html]")
    markdown = Markdown()
    html = markdown.convert(output)
    click.echo(html.strip())


@cli.command(help="Serve web application.")
@click.option("--port", default=8000, show_default=True, help="Port number.")
@paths_argument
def serve(port, paths):
    from pheasant.app.app import App

    app = App(paths)
    app.run(port)

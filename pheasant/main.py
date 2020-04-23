import os
import sys

import click

from pheasant import __version__
from pheasant.core.page import Pages

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
    pages = Pages(paths, ext).collect()

    length = len(pages)
    click.secho(f"collected {length} files.", bold=True)

    if length > max:  # pragma: no cover
        click.secho("Too many files. Aborted.", fg="yellow")
        sys.exit()

    if force:
        for page in pages:
            if page.has_cache:
                page.cache.delete()
                click.echo(page.cache.path + " was deleted.")

    from pheasant.core.pheasant import Pheasant

    converter = Pheasant(restart=restart, shutdown=shutdown, verbose=verbose)
    converter.jupyter.safe = True
    converter.convert_from_files(page.path for page in pages)
    click.secho(f"{converter.log.info}", bold=True)


@cli.command(help="Convert source files to rendered Markdown.")
@click.option("-r", "--restart", is_flag=True, help="Restart kernel after run.")
@click.option("-s", "--shutdown", is_flag=True, help="Shutdown kernel after run.")
@click.option("-f", "--force", is_flag=True, help="Delete cache and run.")
@click.option(
    "-v", "--verbose", count=True, help="Print input codes and/or outputs from kernel."
)
@ext_option
@max_option
@paths_argument
def convert(paths, ext, max, restart, shutdown, force, verbose):
    pages = Pages(paths, ext).collect()

    length = len(pages)
    click.secho(f"collected {length} files.", bold=True)

    if length > max:  # pragma: no cover
        click.secho("Too many files. Aborted.", fg="yellow")
        sys.exit()

    if force:
        for page in pages:
            if page.has_cache:
                page.cache.delete()
                click.echo(page.cache.path + " was deleted.")

    from pheasant.core.pheasant import Pheasant

    converter = Pheasant(restart=restart, shutdown=shutdown, verbose=verbose)
    converter.jupyter.safe = True
    outputs = converter.convert_from_files(page.path for page in pages)
    for page, output in zip(pages, outputs):
        path = page.path.replace(".py", ".md").replace(".md", ".out.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)


@cli.command(help="List source files.")
@ext_option
@paths_argument
def list(paths, ext):
    pages = Pages(paths, ext).collect()

    def size(cache):
        size = cache.size / 1024
        if size > 1024:
            size /= 1024
            return f"{size:.01f}MB"
        else:
            return f"{size:.01f}KB"

    for page in pages:
        click.echo(
            ("* " if page.modified else "  ")
            + page.path
            + (f" (cached, {size(page.cache)})" if page.has_cache else "")
        )

    click.secho(f"collected {len(pages)} files.", bold=True)


@cli.command(help="Delete caches for source files.")
@click.option("-y", "--yes", is_flag=True, help="Do not ask for confirmation.")
@ext_option
@paths_argument
def clean(paths, ext, yes):
    pages = Pages(paths, ext).collect()
    caches = [page.cache for page in pages if page.has_cache]

    if not caches:
        click.secho("No cache found. Aborted.", bold=True)
        sys.exit()

    for cache in caches:
        click.echo(cache.path)

    click.secho(f"collected {len(caches)} files.", bold=True)

    if not yes:
        click.confirm(
            "Are you sure you want to delete the caches for these files?", abort=True
        )

    for cache in caches:
        cache.delete()
        click.echo(cache.path + " was deleted.")


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
@ext_option
def serve(port, paths, ext):
    from pheasant.app.app import App

    app = App(paths, ext)
    app.run(port=port)

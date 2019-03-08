import glob
import logging
import os

import click

# import pypandoc
import pheasant
from pheasant.converters import convert

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@click.command()
@click.argument("inputs", nargs=-1)
@click.option("--format", "-f", default=None)
@click.option("--output", "-o", default=None)
@click.option("--to", "-t", default=None)
@click.option("--verbose", "-v", is_flag=True)
@click.option("--version", is_flag=True)
def cli(inputs, format, output, to, verbose, version):
    if version:
        print(f"Pheasant version: {pheasant.__version__}")
        return

    # FIXME
    if verbose:
        logging.basicConfig(level=logging.INFO)

    config = default_config()
    markdown = ""
    for path in get_file(inputs):
        markdown += convert(path, config)

    print(markdown)


def get_file(inputs):
    for input in inputs:
        paths = glob.glob(input)
        for path in paths:
            if os.path.isfile(path):
                yield path


def default_config():
    config = {}
    for converter in ["jupyter", "number", "code"]:
        config[converter] = {"enabled": True}
    return config


def main():
    cli()


if __name__ == "__main__":
    main()

import os
import sys

import click

from pheasant import __version__

pgk_dir = os.path.dirname(os.path.abspath(__file__))


@click.command()
@click.version_option(
    f"{__version__} from {pgk_dir} (Python {sys.version[:3]}).", "-V", "--version"
)
def cli(version):
    """Pheasant command"""


if __name__ == "__main__":  # pragma: no cover
    cli()

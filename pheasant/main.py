import os
import sys

import click

import pheasant


@click.command()
@click.option("--version", is_flag=True)
def cli(version):
    if version:
        print_version()
        return


def print_version():
    pgk_dir = os.path.dirname(os.path.abspath(__file__))
    print(
        f"pheasant, version {pheasant.__version__} from "
        f"{pgk_dir} (Python {sys.version[:3]})."
    )


def main():
    cli()


if __name__ == "__main__":
    main()

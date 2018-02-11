import logging

import click
import pheasant


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', is_flag=True, help='Show version.')
def cli(context, version):
    if version:
        click.echo(f'pheasant version: {pheasant.__version__}')
    else:
        if context.invoked_subcommand is None:
            click.echo(context.get_help())


def main():
    cli()


if __name__ == '__main__':
    main()

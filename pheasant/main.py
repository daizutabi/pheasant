import logging
import os
from pprint import pprint

import click
import pheasant

from pheasant.core.markdown import convert as convert_markdown
from pheasant.core.notebook import convert as convert_notebook
from pheasant.core.client import find_kernel_names


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @click.argument('content', nargs=-1, type=click.Path(exists=True))
# @click.option('--host', '-h', default='localhost', help='Host name.')
# @click.option('--port', '-p', default='8000', help='Port number.')
# @click.option('--open_url', '-o', is_flag=True, help='Open default browser.')
# @click.option('--absolute', '-a', is_flag=True, help='Set absolute URLs.')


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--version', is_flag=True, help='Show version.')
def cli(context, version):
    if version:
        click.echo(f'pheasant version: {pheasant.__version__}')
    else:
        if context.invoked_subcommand is None:
            click.echo(context.get_help())


@cli.command(name='convert', help='Convert a Markdown or Jupyter notebook.')
@click.argument('filename', required=True)
@click.option('--output_format', '-f',
              type=click.Choice(['html', 'markdown', 'notebook']),
              help='Output format.')
def convert_command(filename, output_format):
    if not os.path.exists(filename):
        click.echo(f'Could not find a file: {filename}')
        return

    if filename.endswith('.ipynb'):
        markdown = convert_notebook(filename, output=output_format)
    else:
        markdown = convert_markdown(filename, output=output_format)
    print(markdown)


@cli.command(help='Show language:kernel_name infomation.')
def kernelname():
    language_kernels = find_kernel_names()
    language_len = max(len(language) for language in language_kernels) + 1
    for language in language_kernels:
        for k, kernel_name in enumerate(language_kernels[language]):
            if k == 0:
                print('- ' + language + ':' +
                      ' ' * (language_len - len(language)),
                      kernel_name)
            else:
                print(' ' * (language_len + 3), kernel_name)


def main():
    cli()


if __name__ == '__main__':
    main()

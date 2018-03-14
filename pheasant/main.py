import glob
import logging
import os

import click
import pypandoc
from pheasant.converters import convert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--format', '-f', default=None)
@click.option('--output', '-o', default=None)
@click.option('--to', '-t', default=None)
@click.argument('inputs', nargs=-1)
def cli(inputs, format, output, to):
    config = default_config()
    markdown = ''
    for path in get_file(inputs):
        markdown += convert(path, config)

    pdoc_args = ['--self-contained']  # ['--mathjax', '--smart']
    html = pypandoc.convert_text(markdown, 'md', format='html',
                                 extra_args=pdoc_args)

    print(html)


def get_file(inputs):
    for input in inputs:
        paths = glob.glob(input)
        for path in paths:
            if os.path.isfile(path):
                yield path


def default_config():
    config = {}
    for converter in ['jupyter', 'number', 'code']:
        config[converter] = {'enabled': True}
    return config


def main():
    cli()


if __name__ == '__main__':
    main()

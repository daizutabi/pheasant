import click
import pheasant


@click.command()
# @click.argument('content', nargs=-1, type=click.Path(exists=True))
# @click.option('--host', '-h', default='localhost', help='Host name.')
# @click.option('--port', '-p', default='8000', help='Port number.')
# @click.option('--open_url', '-o', is_flag=True, help='Open default browser.')
# @click.option('--absolute', '-a', is_flag=True, help='Set absolute URLs.')
@click.option('--version', is_flag=True, help='Show version.')
def cli(version):
    if version:
        print('pheasant version:', pheasant.__version__)
        return
    # content = content[0] if content else '.'
    # serve(content, host, port, open_url, not absolute)


def main():
    cli()


if __name__ == '__main__':
    main()

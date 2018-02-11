from click.testing import CliRunner

from pheasant.main import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert result.output.startswith('pheasant version: ')

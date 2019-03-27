from click.testing import CliRunner

from pheasant import __version__
from pheasant.main import cli


def test_main_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output

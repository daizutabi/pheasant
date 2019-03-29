from click.testing import CliRunner

from pheasant import __version__
from pheasant.main import cli


def test_main_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_main_convert():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("example.md", "w") as f:
            f.write("# Title\n## Section\n")

        result = runner.invoke(cli, ["example.md"])
        assert result.exit_code == 0
        assert '<span class="number">1</span>' in result.output
        assert '<span class="number">1.1</span>' in result.output


def test_main_prompt():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, input="```python\n2*3\n```\n\n")
        assert result.exit_code == 0
        assert "[Markdown]" in result.output
        assert "[HTML]" in result.output
        assert '<code class="python">2*3</code>' in result.output
        assert '<code class="text">6</code>' in result.output

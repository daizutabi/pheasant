from click.testing import CliRunner

from pheasant import __version__
from pheasant.main import cli
from pheasant.renderers.jupyter.kernel import kernels


def test_main_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_main_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("example.md", "w") as f:
            f.write("# Title\n## Section\n```python\n1\n```\n")

        result = runner.invoke(cli, ["run", "example.md"])
        assert result.exit_code == 0
        assert len(kernels.kernels) == 1
        result = runner.invoke(cli, ["run", "example.md", "--shutdown"])
        assert result.exit_code == 0
        assert len(kernels.kernels) == 0
        result = runner.invoke(cli, ["run", "example.md", "--force", "-vv"])
        assert result.exit_code == 0
        assert len(kernels.kernels) == 1

        result = runner.invoke(cli, ["list"])
        assert "example.md (cached," in result.output
        result = runner.invoke(cli, ["clean"], input="n\n")
        assert "Aborted" in result.output
        result = runner.invoke(cli, ["clean"], input="y\n")
        assert ".pheasant_cache" in result.output
        assert "example.md.cache was deleted." in result.output
        result = runner.invoke(cli, ["clean", "--yes"])
        assert "No cache found. Aborted." in result.output


def test_main_prompt():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, input="```python\n2*3\n```\n\n")
        assert result.exit_code == 0
        assert "[markdown]" in result.output
        assert "[html]" in result.output
        assert '<code class="python">2*3</code>' in result.output
        assert '<code class="nohighlight">6</code>' in result.output


def test_main_script():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['python'], input="print('abc')\n\n")
        assert result.exit_code == 0
        assert "[source]" in result.output
        assert "[markdown]" in result.output
        assert "[html]" in result.output
        assert '<code class="python">print(&#39;abc&#39;)</code>' in result.output
        assert '<code class="nohighlight">abc</code>' in result.output

from pheasant.renderers.jupyter.jupyter import replace_for_display
from pheasant.renderers.jupyter.display import extra_html


def test_render_inline_option(jupyter):
    jupyter.execute("import holoviews as hv")
    jupyter.execute("from bokeh.plotting import figure")
    jupyter.execute("import altair as alt")
    jupyter.execute("import pandas as pd")

    jupyter.execute("plot = figure(plot_width=250, plot_height=250)")
    output = jupyter.parse("```python inline\nplot\n```\n")
    assert '<div class="cell jupyter display"' in output
    assert jupyter.cache[-1].extra_module == "bokeh"

    output = jupyter.parse("```python inline\nhv.Curve(([1,2],[3,4]))\n```\n")
    assert '<div class="cell jupyter display"' in output
    assert jupyter.cache[-1].extra_module == "holoviews"

    jupyter.execute(
        (
            "source = pd.DataFrame({"
            "'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],"
            "'b': [14, 55, 43, 91, 81, 53, 19, 87, 52]})"
        )
    )

    output = jupyter.parse(
        (
            "```python inline\nalt."
            "Chart(source).mark_bar().encode(x='a', y='b')\n```\n"
        )
    )
    assert "document.addEventListener" in output
    assert jupyter.cache[-1].extra_module == "altair"

    _ = jupyter.parse("```python inline\nplot\n```\n")


def test_render_extra_modules_and_html(jupyter):
    extra_modules = set(jupyter.get_extra_modules())
    assert "bokeh" in extra_modules
    assert "holoviews" in extra_modules
    assert "altair" in extra_modules

    extra = extra_html(extra_modules)
    assert "bokeh" in extra
    assert "HoloView" in extra
    assert "vega" in extra


def test_replace_for_display():
    def replace(output):
        output = output.replace("pheasant.renderers.jupyter.display.", "")
        return output.replace("__pheasant_dummy__", "D")

    assert replace_for_display("a=1") == "a=1"
    assert replace(replace_for_display("a")) == 'D = a\ndisplay(D, output="markdown")'
    assert replace(replace_for_display("^a")) == 'D = a\ndisplay(D, output="html")'
    assert replace_for_display("for k:\n  a") == "for k:\n  a"


def test_render_no_kernel(jupyter):
    assert jupyter.execute("a", language="abc") == []


def test_render_without_language(jupyter):
    output = jupyter.parse("```\n2*3\n```\n")
    assert '<code class="python">6</code></pre></div>' in output


def test_render_debug_option(jupyter):
    output = jupyter.parse("```python debug\n2*3\n```\n")
    assert "pheasant.renderers.jupyter.display.display(__pheasant_dummy__" in output
    assert "[{&#39;type&#39;: &#39;execute_result&#39;, &#39;data&#39;" in output


def test_render_latex(jupyter):
    jupyter.execute("import sympy")
    output = jupyter.parse("```python\nx=sympy.symbols('x')\nx**2\n```\n")
    assert "$$x^{2}$$" in output


def test_render_fenced_code_with_option(jupyter):
    from pheasant.renderers.jupyter.jupyter import Jupyter

    jupyter = Jupyter()
    output = jupyter.parse("```python abc\n# option: def ghi\nprint(1)\n```\n")
    assert 'class="python">print(1)' in output
    assert "(abc def ghi)" in output

    output = jupyter.parse("```python\n# option: def ghi\nprint(1)\n```\n")
    assert "(def ghi)" in output


def test_render_find_all(jupyter):
    source = "{{2*3}}\n```python\n1\n```\n{{2}}\n```python\n1\n```\n"
    assert len(jupyter.findall(source)) == 4

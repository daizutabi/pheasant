from datetime import timedelta

from pheasant.renderers.jupyter.jupyter import (format_timedelta,
                                                replace_for_display)


def test_format_timedelta():
    assert format_timedelta(timedelta(days=1, seconds=100)) == "24h1min40s"
    assert format_timedelta(timedelta(seconds=3670)) == "1h1min10s"
    assert format_timedelta(timedelta(seconds=2670)) == "44min30s"
    assert format_timedelta(timedelta(seconds=59.564)) == "59.6s"
    assert format_timedelta(timedelta(seconds=9.3)) == "9.30s"
    assert format_timedelta(timedelta(seconds=0.123)) == "123ms"
    assert format_timedelta(timedelta(seconds=0.0453)) == "45.3ms"
    assert format_timedelta(timedelta(seconds=0.006544)) == "6.54ms"
    assert format_timedelta(timedelta(seconds=3.46e-4)) == "346us"
    assert format_timedelta(timedelta(seconds=3.42e-5)) == "34us"
    assert format_timedelta(timedelta(seconds=5.934e-6)) == "6us"
    assert format_timedelta(timedelta(seconds=5.934e-7)) == "1us"
    assert format_timedelta(timedelta(seconds=3.934e-7)) == "<1us"


def test_render_inline_option(jupyter):
    jupyter.execute("import holoviews as hv")
    jupyter.execute("from bokeh.plotting import figure")
    jupyter.execute("import altair as alt")
    jupyter.execute("import pandas as pd")

    jupyter.execute("plot = figure(plot_width=250, plot_height=250)")
    output = jupyter.parse("```python inline\nplot\n```\n")
    assert '<div class="cell jupyter display"' in output
    assert "bokeh" in jupyter.meta[""]["extra_module"]

    output = jupyter.parse("```python inline\nhv.Curve(([1,2],[3,4]))\n```\n")
    assert '<div class="cell jupyter display"' in output
    assert "holoviews" in jupyter.meta[""]["extra_module"]

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
    assert "altair" in jupyter.meta[""]["extra_module"]

    _ = jupyter.parse("```python inline\nplot\n```\n")


def test_render_extra_html(jupyter):
    extra = jupyter.extra_html
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


def test_render_fenced_code_with_option():
    from pheasant.renderers.jupyter.jupyter import Jupyter

    jupyter = Jupyter()
    output = jupyter.parse("```python abc\n# option: def ghi\nprint(1)\n```\n")
    assert 'class="python">print(1)' in output
    assert "(abc def ghi)" in output

    output = jupyter.parse("```python\n# option: def ghi\nprint(1)\n```\n")
    assert "(def ghi)" in output


def test_render_bare_execute_count(jupyter):
    source = "{{2*3}}\n```python\n1\n```\n{{2}}\n```python\n1\n```\n"
    assert jupyter.bare_execute_count(source) == 4

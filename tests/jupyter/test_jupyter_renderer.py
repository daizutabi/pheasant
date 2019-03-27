from datetime import timedelta

from pheasant.jupyter.renderer import format_timedelta, replace_for_display


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
    from pheasant.jupyter.renderer import Jupyter

    jupyter = Jupyter()
    jupyter.execute("import pheasant.jupyter.display")
    jupyter.execute("import holoviews as hv")
    jupyter.execute("from bokeh.plotting import figure")

    jupyter.execute("plot = figure(plot_width=250, plot_height=250)")
    output = jupyter.parse("```python inline\nplot\n```\n")
    assert '<div class="display"' in output
    assert len(jupyter.meta["."]["extra_css"]) == 3
    assert jupyter.meta["."]["extra_module"] == ["bokeh"]

    output = jupyter.parse("```python inline\nhv.Curve(([1,2],[3,4]))\n```\n")
    assert '<div class="display"' in output
    assert len(jupyter.meta["."]["extra_css"]) == 5
    assert "bokeh" in jupyter.meta["."]["extra_module"] == ["bokeh", "holoviews"]
    _ = jupyter.parse("```python inline\nhv.Curve(([1,2],[3,4]))\n```\n")
    assert len(jupyter.meta["."]["extra_css"]) == 5
    assert "bokeh" in jupyter.meta["."]["extra_module"] == ["bokeh", "holoviews"]


def test_replace_for_display():
    def replace(output):
        return output.replace("pheasant.jupyter.display.", "")

    assert replace(replace_for_display("a")) == 'display(a, output="markdown")'
    assert replace_for_display("for k:\n  a") == "for k:\n  a"

    output = replace(replace_for_display("b = 1;a = b", skip_equal=False))
    assert output == 'b = 1\na = b\ndisplay(a, output="markdown")'


def test_render_no_kernel(jupyter):
    assert jupyter.execute("a", language="abc") == []

from pheasant.core.parser import rename_pattern, render_name


def test_render_name_function():
    def function():
        pass

    assert render_name(function) == "function"

    def render_function():
        pass

    assert render_name(function) == "function"


def test_render_name_method():
    class Renderer:
        def method(self):
            pass

        def render_method(self):
            pass

    renderer = Renderer()

    assert render_name(renderer.method) == "renderer__method"
    assert render_name(renderer.render_method) == "renderer__method"


def test_render_name_method_with_name_and_postfix():
    class Renderer:
        def __init__(self, name):
            self.name = name

        def method(self):
            pass

        def render_method(self):
            pass

    renderer = Renderer("example")

    assert render_name(renderer.method, "first") == "renderer__example__method__first"
    assert (
        render_name(renderer.render_method, "second")
        == "renderer__example__method__second"
    )


def test_rename_pattern():
    pattern = r"(?P<prefix>#+) (?P<title>.*?)"
    name = "render"

    rename_pattern(pattern, name)
    assert (
        rename_pattern(pattern, name)
        == "(?P<render>(?P<render___prefix>#+) (?P<render___title>.*?))"
    )

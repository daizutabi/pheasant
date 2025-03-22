from pheasant.core.base import get_render_name, rename_pattern


def test_render_name_function():
    def function():
        pass

    assert get_render_name(function) == "function"

    def render_function():
        pass

    assert get_render_name(function) == "function"


def test_render_name_method():
    class Renderer:
        def method(self):
            pass

        def render_method(self):
            pass

    renderer = Renderer()

    assert get_render_name(renderer.method) == "renderer__method"
    assert get_render_name(renderer.render_method) == "renderer__method"


def test_render_name_method_with_name():
    class Renderer:
        def __init__(self, name):
            self.name = name

        def method(self):
            pass

        def render_method(self):
            pass

    renderer = Renderer("example")

    assert get_render_name(renderer.method) == "renderer__example__method"


def test_rename_pattern():
    pattern = r"(?P<prefix>#+) (?P<title>.*?)"
    name = "render"

    rename_pattern(pattern, name)
    assert (
        rename_pattern(pattern, name)
        == "(?P<render>(?P<render___prefix>#+) (?P<render___title>.*?))"
    )

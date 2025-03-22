from pheasant.utils.progress import bar, progress_bar_factory
import sys


def test_bar_without_multi():
    line = bar(0, 0, 0, 10, "start", "ABC")
    assert line.count("/") == 1


def test_progress_bar():
    progress_bar = progress_bar_factory(total=10, multi=1, init="start")

    def print_with_newline():
        assert progress_bar.parent.stream.on_bar is True
        print("abc")
        assert progress_bar.parent.stream.on_bar is False
        return "hello"

    def print_without_newline():
        assert progress_bar.parent.stream.on_bar is True
        print("abc", end="")
        assert progress_bar.parent.stream.on_bar is False
        return "hello"

    def stdout_write_flush():
        assert progress_bar.parent.stream.on_bar is True
        sys.stdout.write("abc")
        sys.stdout.flush()
        assert progress_bar.parent.stream.on_bar is False
        return "hello"

    assert progress_bar.progress(print_with_newline) == 'hello'
    assert progress_bar.count == 1
    assert progress_bar.parent.stream.on_bar is True

    assert progress_bar.progress(print_without_newline) == 'hello'
    assert progress_bar.count == 2
    assert progress_bar.parent.stream.on_bar is True

    assert progress_bar.progress(stdout_write_flush) == 'hello'
    assert progress_bar.count == 3
    assert progress_bar.parent.stream.on_bar is True

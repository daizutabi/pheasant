from dataclasses import field, is_dataclass
from datetime import timedelta

from pheasant.core.base import Base, format_timedelta_human, make_cell_class


def test_base_repr():
    assert is_dataclass(Base)
    a = Base()
    assert is_dataclass(a)
    assert repr(a) == "<Base#base>"
    a = Base("abc")
    assert repr(a) == "<Base#abc>"


class A(Base):
    age: int = 0
    values: list = field(default_factory=list)

    def __post_repr__(self):
        return "".join([f"{self.age}", f"{self.config}", f"{self.values}"])


def test_base_inherit():
    assert is_dataclass(A)
    a = A(age=123)
    assert is_dataclass(a)
    assert repr(a) == "<A#a[123{}[]]>"
    a = A("abc", age=3, config={"key": "value"}, values=[1, 2])
    assert repr(a) == "<A#abc[3{'key': 'value'}[1, 2]]>"


def test_update_config():
    a = A(config={"A": 1, "B": ["a"], "C": {"a": 1, "b": [1, 2]}})
    a._update("config", {"A": 2, "B": ["b"], "C": {"a": 2, "b": [3], "c": 0}, "D": "a"})
    assert a.config["A"] == 2
    assert a.config["B"] == ["a", "b"]
    assert a.config["C"] == {"a": 2, "b": [3], "c": 0}
    assert a.config["D"] == "a"


def test_core_make_cell_class():
    def func(context, spliter, parser):
        pass

    cell_class = make_cell_class("pattern", func, "render_name")
    cell = cell_class("source", "match", "output", {"a": "1"})
    assert cell.source == "source"
    assert cell.match == "match"
    assert cell.output == "output"
    assert cell.context == {"a": "1"}
    assert cell.render_name == "render_name"


def test_format_timedelta():
    assert format_timedelta_human(timedelta(days=1, seconds=100)) == "24h1min40s"
    assert format_timedelta_human(timedelta(seconds=3670)) == "1h1min10s"
    assert format_timedelta_human(timedelta(seconds=2670)) == "44min30s"
    assert format_timedelta_human(timedelta(seconds=59.564)) == "59.6s"
    assert format_timedelta_human(timedelta(seconds=9.3)) == "9.30s"
    assert format_timedelta_human(timedelta(seconds=0.123)) == "123ms"
    assert format_timedelta_human(timedelta(seconds=0.0453)) == "45.3ms"
    assert format_timedelta_human(timedelta(seconds=0.006544)) == "6.54ms"
    assert format_timedelta_human(timedelta(seconds=3.46e-4)) == "346us"
    assert format_timedelta_human(timedelta(seconds=3.42e-5)) == "34us"
    assert format_timedelta_human(timedelta(seconds=5.934e-6)) == "6us"
    assert format_timedelta_human(timedelta(seconds=5.934e-7)) == "1us"

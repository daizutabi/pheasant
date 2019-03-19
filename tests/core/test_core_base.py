from dataclasses import field, is_dataclass

from pheasant.core.base import Base


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

import pytest
from lab_python_fp.field import field
from lab_python_fp.unique import Unique
from lab_python_fp.gen_random import gen_random


def test_field_omits_only_none():
    data = [{"a": 0}, {"a": None}, {}, {"a": False}, {"a": ""}]
    assert list(field(data, "a")) == [0, False, ""]
    assert list(field(data, "a", "b")) == [{"a": 0}, {"a": False}, {"a": ""}]
    with pytest.raises(ValueError):
        list(field(data))


def test_unique_generator_preserves_values():
    assert list(Unique(iter(["А", "а", "Б"]), ignore_case=True)) == ["А", "Б"]
    assert list(Unique(["А", "а"])) == ["А", "а"]
    assert list(Unique([[1], [1], [2]])) == [[1], [2]]


def test_random_bounds_and_empty():
    assert list(gen_random(3, 7, 7)) == [7, 7, 7]
    assert list(gen_random(0, 1, 2)) == []
    values = list(gen_random(100, -2, 2))
    assert len(values) == 100 and all(-2 <= n <= 2 for n in values)
    with pytest.raises(ValueError):
        list(gen_random(-1, 0, 2))

from math import pi
import pytest
from . import Rectangle, Circle, Square
from .figure import Figure
from .color import Color


def test_variant_21():
    assert Rectangle(21, 21, "синий").area() == 441
    assert Square(21).area() == 441
    assert Circle(21, "зелёный").area() == pytest.approx(441 * pi)


def test_inheritance_and_class_name():
    assert isinstance(Square(21), Rectangle)
    assert Square.get_name() == "Квадрат"
    with pytest.raises(TypeError):
        Figure()


@pytest.mark.parametrize("size", [0, -1, float("nan"), float("inf")])
def test_invalid_size(size):
    with pytest.raises(ValueError):
        Circle(size, "зелёный")


def test_color_property_and_representation():
    figure = Square(21)
    figure.color.value = "синий"
    assert "синий" in repr(figure)
    assert "441.0000" in repr(figure)
    with pytest.raises(ValueError):
        Color("")

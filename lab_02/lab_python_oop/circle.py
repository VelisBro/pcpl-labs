from math import pi
from .figure import Figure
from .color import Color


class Circle(Figure):
    name = "Круг"

    def __init__(self, radius, color):
        self.radius = self.positive(radius)
        self.color = Color(color)

    def area(self):
        return pi * self.radius ** 2

    def __repr__(self):
        return "{}: радиус={:g}, цвет={}, площадь={:.4f}".format(
            self.get_name(), self.radius, self.color.value, self.area())

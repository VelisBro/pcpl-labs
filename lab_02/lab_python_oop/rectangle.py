from .figure import Figure
from .color import Color


class Rectangle(Figure):
    name = "Прямоугольник"

    def __init__(self, width, height, color):
        self.width = self.positive(width)
        self.height = self.positive(height)
        self.color = Color(color)

    def area(self):
        return self.width * self.height

    def __repr__(self):
        return "{}: ширина={:g}, высота={:g}, цвет={}, площадь={:.4f}".format(
            self.get_name(), self.width, self.height, self.color.value, self.area())

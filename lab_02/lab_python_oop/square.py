from .rectangle import Rectangle


class Square(Rectangle):
    name = "Квадрат"

    def __init__(self, side, color="красный"):
        super().__init__(side, side, color)

    def __repr__(self):
        return "{}: сторона={:g}, цвет={}, площадь={:.4f}".format(
            self.get_name(), self.width, self.color.value, self.area())

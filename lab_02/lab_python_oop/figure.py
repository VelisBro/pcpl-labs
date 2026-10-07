from abc import ABC, abstractmethod
from math import isfinite


class Figure(ABC):
    name = "Геометрическая фигура"

    @classmethod
    def get_name(cls):
        return cls.name

    @staticmethod
    def positive(value):
        number = float(value)
        if not isfinite(number) or number <= 0:
            raise ValueError("Размер должен быть конечным положительным числом")
        return number

    @abstractmethod
    def area(self):
        raise NotImplementedError

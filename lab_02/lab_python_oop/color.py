class Color:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Цвет должен быть непустой строкой")
        self._value = value.strip()

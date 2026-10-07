"""Задача 3. Итератор, сохраняющий порядок и исходные значения."""


class Unique:
    def __init__(self, items, **kwargs):
        self.items = iter(items)
        self.ignore_case = kwargs.pop("ignore_case", False)
        if kwargs or not isinstance(self.ignore_case, bool):
            raise TypeError("Допустим только bool-параметр ignore_case")
        self.seen = []

    def __iter__(self):
        return self

    def __next__(self):
        for item in self.items:
            key = item.casefold() if self.ignore_case and isinstance(item, str) else item
            if key not in self.seen:
                self.seen.append(key)
                return item
        raise StopIteration


if __name__ == "__main__":
    data = ["a", "A", "b", "B", "a"]
    print(list(Unique(data)))
    print(list(Unique(iter(data), ignore_case=True)))

"""Задача 1. Ленивое извлечение непустых полей."""


def field(items, *args):
    if not args:
        raise ValueError("Укажите хотя бы одно поле")
    for item in items:
        if len(args) == 1:
            value = item.get(args[0])
            if value is not None:
                yield value
        else:
            values = {key: item[key] for key in args if item.get(key) is not None}
            if values:
                yield values


if __name__ == "__main__":
    goods = [{"title": "Ковер", "price": 2000},
             {"title": "Диван для отдыха", "price": None}, {}]
    print(list(field(goods, "title")))
    print(list(field(goods, "title", "price")))

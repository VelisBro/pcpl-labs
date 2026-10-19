"""РК-1. Вариант 21, запросы А. Запуск: python3 rk_01/main.py."""

from operator import itemgetter


class Operator:
    """Оператор: ключ, название, число операндов, основной язык."""

    def __init__(self, id, name, arity, language_id):
        self.id = id
        self.name = name
        self.arity = arity
        self.language_id = language_id


class Language:
    """Язык программирования на стороне «один»."""

    def __init__(self, id, name):
        self.id = id
        self.name = name


class OperatorLanguage:
    """Связь многие-ко-многим по идентификаторам."""

    def __init__(self, operator_id, language_id):
        self.operator_id = operator_id
        self.language_id = language_id


def main():
    # Учебные данные: арность означает число операндов оператора.
    # Основной язык нужен для связи 1:N, а не обозначает происхождение.
    languages = [
        Language(1, "язык Python"),
        Language(2, "язык Rust"),
        Language(3, "язык Ada"),
    ]
    operators = [
        Operator(1, "+", 2, 1),
        Operator(2, "*", 2, 1),
        Operator(3, "not", 1, 3),
        Operator(4, "-", 2, 2),
    ]
    links = [
        OperatorLanguage(1, 1),
        OperatorLanguage(1, 2),
        OperatorLanguage(2, 1),
        OperatorLanguage(3, 3),
        OperatorLanguage(4, 2),
    ]

    one_to_many = [
        (op.name, op.arity, lang.name)
        for lang in languages
        for op in operators
        if op.language_id == lang.id
    ]
    many_to_many = [
        (op.name, op.arity, lang.name)
        for link in links
        for op in operators
        for lang in languages
        if op.id == link.operator_id and lang.id == link.language_id
    ]

    print("РК-1. Вариант 21. Запросы А")
    print("А1. Операторы и языки, сортировка по языкам")
    for row in sorted(one_to_many, key=itemgetter(2, 0)):
        print(row)

    print("\nА2. Суммарная арность по языкам, по убыванию")
    totals = [
        (lang.name, sum(row[1] for row in one_to_many
                        if row[2] == lang.name))
        for lang in languages
        if any(row[2] == lang.name for row in one_to_many)
    ]
    for row in sorted(totals, key=lambda row: (-row[1], row[0])):
        print(row)

    print("\nА3. Слово 'язык' в названии, связь M:N")
    result = {
        lang.name: [name for name, _, language in many_to_many
                    if language == lang.name]
        for lang in languages
        if "язык" in lang.name.casefold().split()
    }
    for language, names in result.items():
        print(f"{language}: {', '.join(names)}")


if __name__ == "__main__":
    main()

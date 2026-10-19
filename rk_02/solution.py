"""Рефакторинг РК-1: неизменяемые данные и чистые функции запросов."""

from dataclasses import dataclass
from operator import itemgetter


@dataclass(frozen=True)
class Operator:
    id: int
    name: str
    arity: int
    language_id: int


@dataclass(frozen=True)
class Language:
    id: int
    name: str


@dataclass(frozen=True)
class OperatorLanguage:
    operator_id: int
    language_id: int


def sample_data():
    """Каждый вызов возвращает отдельные коллекции тестовых данных."""
    return (
        [Operator(1, "+", 2, 1), Operator(2, "*", 2, 1),
         Operator(3, "not", 1, 3), Operator(4, "-", 2, 2)],
        [Language(1, "язык Python"), Language(2, "язык Rust"),
         Language(3, "язык Ada")],
        [OperatorLanguage(1, 1), OperatorLanguage(1, 2),
         OperatorLanguage(2, 1), OperatorLanguage(3, 3),
         OperatorLanguage(4, 2)],
    )


def query_a1(operators, languages):
    """Соединение 1:N; сортировка по языку, затем оператору."""
    return sorted(
        [(op.name, op.arity, lang.name)
         for op in operators for lang in languages
         if op.language_id == lang.id],
        key=itemgetter(2, 0),
    )


def query_a2(operators, languages):
    """Сумма арностей; пустые группы исключены, как в примере условия."""
    totals = [
        (lang.name, sum(op.arity for op in operators
                        if op.language_id == lang.id))
        for lang in languages
        if any(op.language_id == lang.id for op in operators)
    ]
    return sorted(totals, key=lambda row: (-row[1], row[0]))


def query_a3(operators, languages, links):
    """Связь M:N независима от language_id основного языка."""
    return {
        lang.name: [op.name for link in links for op in operators
                    if link.language_id == lang.id
                    and op.id == link.operator_id]
        for lang in languages
        if "язык" in lang.name.casefold().split()
    }


def main():
    operators, languages, links = sample_data()
    for label, result in [
        ("А1", query_a1(operators, languages)),
        ("А2", query_a2(operators, languages)),
        ("А3", query_a3(operators, languages, links)),
    ]:
        print(label)
        if isinstance(result, dict):
            for language, names in result.items():
                print(f"{language}: {', '.join(names)}")
        else:
            for row in result:
                print(row)
        print()


if __name__ == "__main__":
    main()

"""Ровно три модульных теста на стандартном фреймворке unittest."""

import unittest

from rk_02.solution import (
    Language, Operator, OperatorLanguage,
    query_a1, query_a2, query_a3, sample_data,
)


class QueryTests(unittest.TestCase):
    def test_a1_join_and_sort(self):
        operators, languages, _ = sample_data()
        # Вход намеренно перевёрнут: проверяем ключ сортировки.
        self.assertEqual(query_a1(operators[::-1], languages[::-1]), [
            ("not", 1, "язык Ada"),
            ("*", 2, "язык Python"), ("+", 2, "язык Python"),
            ("-", 2, "язык Rust"),
        ])
        self.assertEqual(query_a1([], languages), [])
        self.assertEqual(query_a1(operators, []), [])

    def test_a2_sum_sort_and_empty_groups(self):
        operators, languages, _ = sample_data()
        languages.append(Language(4, "язык C"))
        self.assertEqual(query_a2(operators, languages), [
            ("язык Python", 4), ("язык Rust", 2), ("язык Ada", 1),
        ])
        # Равные суммы упорядочиваются по названию; пустая группа исключена.
        self.assertEqual(query_a2([
            Operator(1, "+", 2, 1), Operator(2, "-", 2, 2),
        ], languages), [("язык Python", 2), ("язык Rust", 2)])
        self.assertEqual(query_a2([], languages), [])

    def test_a3_filter_and_many_to_many(self):
        operators, languages, links = sample_data()
        self.assertEqual(query_a3(operators, languages, links), {
            "язык Python": ["+", "*"], "язык Rust": ["+", "-"],
            "язык Ada": ["not"],
        })
        # '+' связан с Rust через таблицу M:N, хотя его основной язык Python.
        # Проверяем регистр, слово целиком и язык без связанных операторов.
        languages += [Language(4, "ЯЗЫК C"), Language(5, "метаязык")]
        links += [OperatorLanguage(1, 5)]
        result = query_a3(operators, languages, links)
        self.assertEqual(result["ЯЗЫК C"], [])
        self.assertNotIn("метаязык", result)
        self.assertEqual(query_a3([], languages, []), {
            lang.name: [] for lang in languages
            if lang.id != 5
        })


if __name__ == "__main__":
    unittest.main()

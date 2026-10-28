"""Проверки варианта Б18: python3 -m unittest rk_01.test_queries -v."""

import unittest

from rk_01.main import (
    MusicalWork, Orchestra, WorkOrchestra,
    query_b1, query_b2, query_b3, sample_data,
)


class QueryTests(unittest.TestCase):
    def test_b1_sorts_by_work(self):
        works, orchestras, _ = sample_data()
        self.assertEqual(query_b1(works, orchestras), [
            ("Вальс цветов", "Симфонический оркестр"),
            ("Полет шмеля", "Филармонический оркестр"),
            ("Танец рыцарей", "Симфонический оркестр"),
            ("Танец эльфов", "Камерный оркестр"),
        ])

    def test_b2_counts_primary_orchestras(self):
        works, orchestras, _ = sample_data()
        self.assertEqual(query_b2(works, orchestras), [
            ("Камерный оркестр", 1),
            ("Филармонический оркестр", 1),
            ("Симфонический оркестр", 2),
        ])

    def test_b3_uses_many_to_many(self):
        works, orchestras, links = sample_data()
        self.assertEqual(query_b3(works, orchestras, links), [
            ("Вальс цветов", ["Симфонический оркестр", "Камерный оркестр"]),
            ("Танец эльфов", ["Камерный оркестр"]),
        ])

    def test_empty_collections_and_empty_orchestra(self):
        self.assertEqual(query_b1([], []), [])
        self.assertEqual(query_b2([], []), [])
        self.assertEqual(query_b2([], [Orchestra(1, "Пустой")]), [("Пустой", 0)])
        self.assertEqual(query_b3([], [], []), [])

    def test_ids_distinguish_equal_names(self):
        works = [MusicalWork(1, "Танец эльфов", 3, 1),
                 MusicalWork(2, "Танец эльфов", 4, 2)]
        orchestras = [Orchestra(1, "Оркестр"), Orchestra(2, "Оркестр")]
        self.assertEqual(query_b2(works, orchestras), [("Оркестр", 1)] * 2)
        self.assertEqual(query_b3(works, orchestras, [WorkOrchestra(2, 2)]),
                         [("Танец эльфов", []), ("Танец эльфов", ["Оркестр"])])

    def test_suffix_and_missing_links(self):
        works = [MusicalWork(1, "Танец ЭЛЬФОВ", 3, 1),
                 MusicalWork(2, "Вальс цветов весной", 8, 1)]
        self.assertEqual(query_b3(works, [Orchestra(1, "Оркестр")], []),
                         [("Танец ЭЛЬФОВ", [])])


if __name__ == "__main__":
    unittest.main()

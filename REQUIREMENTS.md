# Соответствие условиям

| Работа | Требование | Реализация и проверка |
|---|---|---|
| 1 | Три парадигмы | procedural.py, object_oriented.py, functional.py с match/case |
| 1 | Ввод из аргументов или с клавиатуры, повтор ошибок | common.read_coefficients и тест с ошибочным вводом |
| 1 | Дискриминант и действительные корни | common.run; 30 случаев проверки трёх решений |
| 2 | Виртуальное окружение, внешний пакет | requirements.txt; вызов colorama.init в main.py |
| 2 | Абстрактная фигура, Color.property, наследование | Отдельный модуль для каждого класса в lab_python_oop |
| 2 | repr, format, classmethod, вариант N | N=21; Rectangle, Circle, Square; семь проверок |
| 3 | field, gen_random, Unique, сортировка | Задачи 1–4 в lab_python_fp, отдельные запускаемые файлы |
| 4 | Декоратор, два менеджера, конвейер f1–f4 | Задачи 5–7; filter, map, zip; сортировка без регистра |
| 5 | Минимум 3 теста TDD-фреймворка и 3 BDD | Четыре pytest-теста, три Gherkin-сценария pytest-bdd |
| 5 | Mock как дополнительное задание | Mock ввода и вывода |
| 6 | Хотя бы один шаблон | Factory Method, два конкретных создателя и продукта |
| 6 | TDD-фреймворк, BDD, Mock | pytest, pytest-bdd, unittest.mock |
| Все | Титул, задание, код, экранные формы | report.docx и report.pdf в каждой папке |

## Ссылки на задания

- [ЛР 1](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_intro)
- [ЛР 2](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_oop)
- [ЛР 3–4](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_fp)
- [ЛР 5](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_test)
- [Выбранная ЛР 6](https://github.com/ugapanyuk/BKIT_2021/wiki/lab_python_test)

В шаблоне комментария к Unique на странице задания перепутаны значения ignore_case.
Реализация следует основному тексту и примерам: True объединяет разные регистры.

«TDD-фреймворк» реализован тестами pytest согласно формулировке задания. Журналы
подтверждают результат тестов; утверждение о хронологии разработки по циклу
red–green–refactor не делается.

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
| 5 | Простой Telegram-бот на Python с кнопками | lab_05/main.py; ReplyKeyboardMarkup, Сегодня/Завтра/Неделя, импорт TXT |
| 6 | Telegram-бот на Python, конечный автомат из трёх состояний | lab_06/main.py; SCHEDULE → REMINDER_TIME → CONFIRM; ConversationHandler |
| 5–6 | Учебный ежедневник по запросу пользователя | Персональная SQLite, ЧС/ЗН, ежедневная отправка, отключение и удаление данных |
| 1–4 | Титул, задание, код, экранные формы | report.docx и report.pdf |
| 5–6 | Титул, задание, код, экранные формы | Тексты report.md; реальные экранные формы и DOCX/PDF ещё нужно оформить |

## Ссылки на задания

- [ЛР 1](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_intro)
- [ЛР 2](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_oop)
- [ЛР 3–4](https://github.com/ugapanyuk/BKIT_2022/wiki/lab_python_fp)
- [ЛР 5](https://github.com/ugapanyuk/BKIT_2021/wiki/lab_bot1)
- [ЛР 6](https://github.com/ugapanyuk/BKIT_2021/wiki/lab_bot2)

В шаблоне комментария к Unique на странице задания перепутаны значения ignore_case.
Реализация следует основному тексту и примерам: True объединяет разные регистры.

ЛР 5 и 6 заменены 21.10.2026 по запросу пользователя. Старые работы и их отчёты доступны
в истории Git. Проверки новых ботов выполняются без сети и не подтверждают фактическую
доставку в Telegram: для неё нужны новый токен и проверка реального диалога.

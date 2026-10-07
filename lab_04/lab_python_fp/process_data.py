"""Задача 7. Конвейер обработки вакансий."""
import argparse
import json
import random
from lab_python_fp.field import field
from lab_python_fp.gen_random import gen_random
from lab_python_fp.unique import Unique
from lab_python_fp.print_result import print_result
from lab_python_fp.cm_timer import cm_timer_1


@print_result
def f1(arg):
    return sorted(Unique(field(arg, "job-name"), ignore_case=True), key=str.casefold)


@print_result
def f2(arg):
    return list(filter(lambda title: title.casefold().startswith("программист"), arg))


@print_result
def f3(arg):
    return list(map(lambda title: title + " с опытом Python", arg))


@print_result
def f4(arg):
    return [f"{title}, зарплата {salary} руб." for title, salary in
            zip(arg, gen_random(len(arg), 100000, 200000))]


def main():
    parser = argparse.ArgumentParser(description="Обработка списка вакансий")
    parser.add_argument("path", help="JSON-файл со списком вакансий")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)
    with open(args.path, encoding="utf-8") as source:
        data = json.load(source)
    if not isinstance(data, list):
        parser.error("JSON должен содержать список")
    with cm_timer_1():
        f4(f3(f2(f1(data))))


if __name__ == "__main__":
    main()

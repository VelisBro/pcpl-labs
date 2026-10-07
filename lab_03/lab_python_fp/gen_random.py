"""Задача 2. Генератор целых чисел с включёнными границами."""
import random


def gen_random(num_count, begin, end):
    if num_count < 0 or begin > end:
        raise ValueError("Нужны неотрицательное количество и begin <= end")
    for _ in range(num_count):
        yield random.randint(begin, end)


if __name__ == "__main__":
    random.seed(21)
    print(list(gen_random(5, 1, 3)))

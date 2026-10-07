"""Общий ввод и представление результата трёх реализаций."""
import math
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Solution:
    roots: tuple[float, ...] = ()
    infinite: bool = False


def read_coefficients(args, input_fn=input, output_fn=print):
    values = []
    for index, name in enumerate("ABC"):
        raw = args[index] if index < len(args) else None
        while True:
            if raw is None:
                raw = input_fn(f"{name} = ")
            try:
                value = float(raw)
                if not math.isfinite(value):
                    raise ValueError
                values.append(value)
                break
            except (ValueError, TypeError):
                output_fn(f"Некорректный коэффициент {name}. Введите конечное число.")
                raw = None
    return tuple(values)


def run(solver):
    try:
        a, b, c = read_coefficients(sys.argv[1:])
        result = solver(a, b, c)
        print(f"A = {a:g}; B = {b:g}; C = {c:g}")
        print(f"Дискриминант = {b * b - 4 * a * c:g}")
        if result.infinite:
            print("Решение: любое действительное число")
        elif result.roots:
            print("Действительные корни:", ", ".join(f"{x:.12g}" for x in result.roots))
        else:
            print("Действительных корней нет")
    except (EOFError, KeyboardInterrupt):
        print("\nВвод прерван", file=sys.stderr)
        return 1
    except (ValueError, OverflowError) as error:
        print(f"Ошибка вычисления: {error}", file=sys.stderr)
        return 1
    return 0

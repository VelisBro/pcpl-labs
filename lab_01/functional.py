"""Чистые функции и структурное сопоставление с образцом."""
from math import copysign, sqrt
from common import Solution, run


def square_roots(a, b, c):
    match (a, b, c):
        case (0, 0, _):
            return ()
        case (0, _, _):
            return (-c / b,)
        case _:
            scale = max(abs(a), abs(b), abs(c))
            a, b, c = a / scale, b / scale, c / scale
            match b * b - 4 * a * c:
                case d if d < 0:
                    return ()
                case 0:
                    return (-b / (2 * a),)
                case d:
                    q = -0.5 * (b + copysign(sqrt(d), b))
                    return (q / a, c / q)


def solve(a, b, c):
    match (a, b, c):
        case (0, 0, 0):
            return Solution(infinite=True)
        case _:
            values = map(sqrt, filter(lambda y: y >= 0, square_roots(a, b, c)))
            return Solution(tuple(sorted({x for r in values for x in (-r, r)})))


if __name__ == "__main__":
    raise SystemExit(run(solve))

"""Процедурное решение A*x**4 + B*x**2 + C = 0."""
from math import copysign, sqrt
from common import Solution, run


def solve(a, b, c):
    if a == 0:
        if b == 0:
            return Solution(infinite=c == 0)
        squares = (-c / b,)
    else:
        # Масштабирование снижает вероятность переполнения дискриминанта.
        scale = max(abs(a), abs(b), abs(c))
        a, b, c = a / scale, b / scale, c / scale
        d = b * b - 4 * a * c
        if d < 0:
            return Solution()
        if d == 0:
            squares = (-b / (2 * a),)
        else:
            q = -0.5 * (b + copysign(sqrt(d), b))
            squares = (q / a, c / q)
    roots = set()
    for y in squares:
        if y >= 0:
            roots.update((-sqrt(y), sqrt(y)))
    return Solution(tuple(sorted(roots)))


if __name__ == "__main__":
    raise SystemExit(run(solve))

"""Объект хранит коэффициенты и вычисляет корни уравнения."""
from dataclasses import dataclass
from math import copysign, sqrt
from common import Solution, run


@dataclass(frozen=True)
class BiquadraticEquation:
    a: float
    b: float
    c: float

    @property
    def discriminant(self):
        return self.b ** 2 - 4 * self.a * self.c

    def solve(self):
        a, b, c = self.a, self.b, self.c
        if a == 0 and b == 0:
            return Solution(infinite=c == 0)
        if a == 0:
            squares = (-c / b,)
        else:
            scale = max(abs(a), abs(b), abs(c))
            normalized = BiquadraticEquation(a / scale, b / scale, c / scale)
            d = normalized.discriminant
            if d < 0:
                return Solution()
            if d == 0:
                squares = (-normalized.b / (2 * normalized.a),)
            else:
                q = -0.5 * (normalized.b + copysign(sqrt(d), normalized.b))
                squares = (q / normalized.a, normalized.c / q)
        roots = {sign * sqrt(y) for y in squares if y >= 0 for sign in (-1, 1)}
        return Solution(tuple(sorted(roots)))


if __name__ == "__main__":
    raise SystemExit(run(lambda a, b, c: BiquadraticEquation(a, b, c).solve()))

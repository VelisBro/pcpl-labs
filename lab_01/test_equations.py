import pytest
from procedural import solve as procedural
from functional import solve as functional
from object_oriented import BiquadraticEquation
from common import read_coefficients


@pytest.mark.parametrize("solver", [procedural, functional,
    lambda a, b, c: BiquadraticEquation(a, b, c).solve()])
@pytest.mark.parametrize("coefficients, roots, infinite", [
    ((1, -5, 4), (-2, -1, 1, 2), False),
    ((1, -2, 1), (-1, 1), False),
    ((1, 0, 1), (), False),
    ((1, 5, 4), (), False),
    ((1, 0, -16), (-2, 2), False),
    ((1, -1, 0), (-1, 0, 1), False),
    ((0, 2, -8), (-2, 2), False),
    ((0, 0, 1), (), False),
    ((0, 0, 0), (), True),
    ((1, 0, 0), (0,), False),
])
def test_real_roots(solver, coefficients, roots, infinite):
    result = solver(*coefficients)
    assert result.roots == pytest.approx(roots)
    assert result.infinite is infinite
    a, b, c = coefficients
    for x in result.roots:
        assert a * x ** 4 + b * x ** 2 + c == pytest.approx(0)


def test_invalid_and_missing_coefficients():
    entries = iter(["bad", "1", "4"])
    messages = []
    assert read_coefficients(["nan", "-5"], lambda _: next(entries), messages.append) == (1, -5, 4)
    assert len(messages) == 2

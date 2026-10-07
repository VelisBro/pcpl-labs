import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from procedural import solve

scenarios("features/equation.feature")


@given(parsers.parse("coefficients {a:g}, {b:g}, {c:g}"), target_fixture="coefficients")
def coefficients(a, b, c):
    return a, b, c


@when("I solve the equation", target_fixture="solution")
def solve_equation(coefficients):
    return solve(*coefficients)


@then("the roots are -2, -1, 1, 2")
def four_roots(solution):
    assert solution.roots == pytest.approx((-2, -1, 1, 2))


@then("there are no real roots")
def no_roots(solution):
    assert solution.roots == () and not solution.infinite


@then("every real number is a solution")
def infinite_roots(solution):
    assert solution.infinite

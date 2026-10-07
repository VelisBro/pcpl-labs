"""Тесты функций лабораторной 1 с использованием pytest."""
from unittest.mock import Mock
import pytest
from procedural import solve
from common import read_coefficients


def test_four_roots():
    assert solve(1, -5, 4).roots == pytest.approx((-2, -1, 1, 2))


def test_no_real_roots():
    assert solve(1, 0, 1).roots == ()
    assert not solve(1, 0, 1).infinite


def test_degenerate_identity():
    assert solve(0, 0, 0).infinite


def test_bad_input_with_mock():
    reader = Mock(side_effect=["wrong", "1"])
    writer = Mock()
    assert read_coefficients(["bad", "-5", "4"], reader, writer) == (1, -5, 4)
    assert reader.call_count == 2
    assert writer.call_count == 2

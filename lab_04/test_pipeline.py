import pytest
from unittest.mock import patch
from lab_python_fp.print_result import print_result
from lab_python_fp.cm_timer import cm_timer_1, cm_timer_2
from lab_python_fp.process_data import f1, f2, f3, f4


def test_pipeline():
    data = [{"job-name": "Программист Python"}, {"job-name": "программист python"},
            {"job-name": "Аналитик"}, {}]
    with patch("lab_python_fp.gen_random.random.randint", return_value=150000):
        assert f4(f3(f2(f1(data)))) == [
            "Программист Python с опытом Python, зарплата 150000 руб."]


def test_decorator_preserves_return_and_arguments(capsys):
    @print_result
    def add(a, b=0):
        return {"sum": a + b}
    assert add(2, b=3) == {"sum": 5}
    assert add.__name__ == "add"
    assert capsys.readouterr().out == "add\nsum = 5\n"


@pytest.mark.parametrize("timer", [cm_timer_1, cm_timer_2])
def test_timers_log_and_propagate_exception(timer, capsys):
    with patch("lab_python_fp.cm_timer.perf_counter", side_effect=[10, 15.5]):
        with pytest.raises(RuntimeError):
            with timer():
                raise RuntimeError("failure")
    assert capsys.readouterr().out == "time: 5.500000\n"

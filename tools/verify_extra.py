"""Повторяемая проверка ДЗ и РК. Запуск из корня: python3 tools/verify_extra.py."""
import ast
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rk_02.solution import sample_data, query_a1, query_a2, query_a3


def run(args, cwd=ROOT, expected=0):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    assert result.returncode == expected, result.stdout + result.stderr
    return result.stdout + result.stderr


def save(folder, name, content):
    path = ROOT / folder / "results" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main():
    rk1 = run([sys.executable, "rk_01/main.py"])
    operators, languages, links = sample_data()
    lines = rk1.splitlines()
    rows = [ast.literal_eval(line) for line in lines if line.startswith("(")]
    assert rows == query_a1(operators, languages) + query_a2(operators, languages)
    for lang, names in query_a3(operators, languages, links).items():
        assert f"{lang}: {', '.join(names)}" in lines
    save("rk_01", "demo.txt", "$ python3 rk_01/main.py\n" + rk1)
    save("rk_01", "checks.txt", "Результаты А1, А2, А3 совпали с функциями РК-2.\n")

    rk2 = run([sys.executable, "-m", "rk_02.solution"])
    tests = run([sys.executable, "-m", "unittest", "rk_02.test_queries", "-v"])
    save("rk_02", "demo.txt", "$ python3 -m rk_02.solution\n" + rk2)
    save("rk_02", "tests.txt", tests)

    homework = ROOT / "homework"
    cargo = ["sh", "cargo-local.sh"]
    run(cargo + ["fmt", "--check"], homework)
    lint = run(cargo + ["clippy", "--offline", "--all-targets", "--", "-D", "warnings"], homework)
    rust_tests = run(cargo + ["test", "--offline", "--", "--test-threads=1"], homework)
    run(cargo + ["build", "--offline"], homework)
    executable = str(homework / "target" / "debug" / "grade_analyzer")
    output = run([executable, "data/students.csv"], homework)
    assert "1. Сидорова: 5.00" in output
    assert "2: 1\n3: 3\n4: 5\n5: 6\n" in output
    invalid = run([executable, "data/invalid.csv"], homework, 1)
    assert "строка 1: оценка вне диапазона 2..5" in invalid
    missing = run([executable, "data/missing.csv"], homework, 1)
    assert "не удалось прочитать" in missing
    no_args = run([executable], homework, 1)
    too_many = run([executable, "a", "b"], homework, 1)
    help_output = run([executable, "--help"], homework)
    assert "Формат строки" in help_output
    assert "один путь" in no_args and "один путь" in too_many
    save("homework", "demo.txt", "$ cargo run --offline -- data/students.csv\n" + output
         + "\n$ cargo run --offline -- data/invalid.csv\n" + invalid
         + "Код возврата: 1\n\n$ cargo run --offline -- --help\n" + help_output)
    save("homework", "tests.txt", rust_tests)
    save("homework", "checks.txt", "cargo fmt --check: OK\n" + lint
         + "CLI: обычный файл, ошибочная оценка, отсутствующий файл,\n"
           "нет аргументов, лишние аргументы, --help: 6 проверок OK.\n")
    print("РК-1: три запроса проверены; РК-2: 3 теста; Rust: 6 тестов и 6 CLI-проверок OK.")


if __name__ == "__main__":
    main()

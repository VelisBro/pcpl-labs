"""Запустить примеры и тесты, сохранить фактический stdout без ANSI-кодов."""
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def execute(args, stdin=None):
    completed = subprocess.run([PYTHON, *args], cwd=ROOT, input=stdin,
        text=True, encoding="utf-8", capture_output=True,
        env={**os.environ, "NO_COLOR": "1"})
    text = "$ python " + " ".join(args) + "\n"
    if stdin is not None:
        text += "Ввод с клавиатуры: " + repr(stdin) + "\n"
    text += completed.stdout + completed.stderr
    if completed.returncode:
        raise RuntimeError(text)
    return text


def main():
    commands = {
        1: [([f"lab_01/{name}.py", "1", "-5", "4"], None)
            for name in ("procedural", "object_oriented", "functional")] + [
            (["lab_01/procedural.py", "1", "0", "1"], None),
            (["lab_01/procedural.py", "0", "0", "0"], None),
            (["lab_01/procedural.py", "bad", "-5", "4"], "oops\n1\n")],
        2: [(["lab_02/main.py", "--variant", "21"], None)],
        3: [([f"lab_03/lab_python_fp/{name}.py"], None)
            for name in ("field", "gen_random", "unique", "sort")],
        4: [([f"lab_04/lab_python_fp/{name}.py"], None)
            for name in ("print_result", "cm_timer")] + [
            (["lab_04/main.py", "lab_04/data/demo.json", "--seed", "21"], None)],
        5: [(["-m", "pytest", "lab_05", "-v", "--tb=short"], None)],
        6: [(["lab_06/main.py"], None)],
    }
    for number, cases in commands.items():
        target = ROOT / f"lab_{number:02}" / "results"
        target.mkdir(exist_ok=True)
        (target / "demo.txt").write_text("\n".join(execute(*case) for case in cases), encoding="utf-8")
        (target / "tests.txt").write_text(execute([
            "-m", "pytest", f"lab_{number:02}", "-v", "--tb=short"]), encoding="utf-8")
    (ROOT / "lab_04/results/full_data.txt").write_text(execute([
        "lab_04/main.py", "lab_04/data/jobs.json", "--seed", "21"]), encoding="utf-8")
    target = ROOT / "validation"
    target.mkdir(exist_ok=True)
    (target / "tests.txt").write_text(execute(["-m", "pytest", "-v", "--tb=short"]), encoding="utf-8")
    (target / "environment.txt").write_text(
        f"Python {platform.python_version()}\nPlatform: {platform.system()} {platform.machine()}\n"
        + execute(["-m", "pip", "freeze"]), encoding="utf-8")
    print("Сохранены журналы шести работ и общего прогона")


if __name__ == "__main__":
    main()

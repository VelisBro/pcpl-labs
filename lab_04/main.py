"""Запуск из любой рабочей директории с модулями лабораторной 3."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab_03"))
from lab_python_fp.process_data import main


if __name__ == "__main__":
    main()

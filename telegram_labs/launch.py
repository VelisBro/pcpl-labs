"""Первый запуск без редактирования кода и без показа токена в терминале."""
import argparse
from getpass import getpass
from importlib import metadata
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="Запуск учебного ежедневника")
    parser.add_argument("--lab", type=int, choices=(5, 6), default=6)
    parser.add_argument("--configure", action="store_true", help="Ввести новый токен")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("Нужен Python 3.10 или новее.")
    requirements = ROOT / "requirements.txt"
    install = False
    for line in requirements.read_text().splitlines():
        name, version = line.split("==")
        try:
            install |= metadata.version(name.split("[")[0]) != version
        except metadata.PackageNotFoundError:
            install = True
    if install:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], check=True)
    from dotenv import dotenv_values, set_key

    config = ROOT / "telegram_labs/.env"
    saved = dotenv_values(config).get("BOT_TOKEN", "")
    effective = os.getenv("BOT_TOKEN") or saved
    if args.configure or not effective or effective == "PASTE_NEW_TOKEN_HERE":
        print("Введи новый токен BotFather после /revoke. Ввод скрыт, символы не отображаются.")
        token = getpass("Токен: ").strip()
        if not re.fullmatch(r"\d+:[A-Za-z0-9_-]{20,}", token):
            raise SystemExit("Формат токена не распознан. Запусти ещё раз и вставь токен целиком.")
        config.touch(mode=0o600, exist_ok=True)
        config.chmod(0o600)
        set_key(config, "BOT_TOKEN", token)
        set_key(config, "BOT_TIMEZONE", "Europe/Moscow")
        # Явный --configure должен заменить и переменную окружения текущего запуска.
        os.environ["BOT_TOKEN"] = token
        print("Настройки сохранены локально. Токен не включается в Git.")
    print(f"Лабораторная №{args.lab}. Открой @velisbro_study_diary_bot и отправь /start.")
    completed = subprocess.run([sys.executable, str(ROOT / f"lab_{args.lab:02}/main.py")], cwd=ROOT)
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nЗапуск отменён.")

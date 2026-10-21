"""Воспроизводимый сценарий через настоящий диспетчер с локальным Bot API."""
import asyncio
from datetime import date
from pathlib import Path
import sys
import tempfile

from telegram_labs.app import TODAY
from telegram_labs.schedule import parse_schedule
from telegram_labs.testing import OfflineTelegram, incoming


async def demo(lab: int):
    if lab == 5:
        from lab_05.main import build_application
    else:
        from lab_06.main import SAVE, build_application
    root = Path(__file__).resolve().parents[1]
    schedule_text = (root / "telegram_labs/data/iu5_32b.txt").read_text(encoding="utf-8")
    transport = OfflineTelegram()
    with tempfile.TemporaryDirectory() as folder:
        app = build_application("123456789:offline_demo", Path(folder) / "demo.sqlite3", transport)
        async with app:
            print("ЛОКАЛЬНАЯ ПРОВЕРКА. Telegram API заменён тестовым транспортом.\n")
            steps = ["/start", "/upload", "[файл iu5_32b.txt]"]
            if lab == 6:
                steps += ["07:00", SAVE]
            steps += [TODAY, "/notify 07:30", "/off"]
            for i, text in enumerate(steps, 1):
                print("СТУДЕНТ:", text)
                before = len(transport.messages)
                if text.startswith("[файл"):
                    transport.file_content = schedule_text.encode("utf-8")
                    update = incoming(app.bot, update_id=i,
                                      document={"file_name": "iu5_32b.txt", "file_size": len(transport.file_content)})
                else:
                    update = incoming(app.bot, text, update_id=i)
                await app.process_update(update)
                for message in transport.messages[before:]:
                    print("БОТ:\n" + message["text"])
                print()
    print("ПРОВЕРКА ЧЕРЕДОВАНИЯ ПО ДАТАМ\n")
    schedule = parse_schedule(schedule_text)
    for index, day in enumerate((date(2026, 10, 21), date(2026, 10, 28))):
        if index:
            print()
        print(schedule.render_day(day))


if __name__ == "__main__":
    asyncio.run(demo(int(sys.argv[1]) if len(sys.argv) > 1 else 6))

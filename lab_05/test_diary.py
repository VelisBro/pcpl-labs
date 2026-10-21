import asyncio
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from lab_05.main import build_application
from telegram_labs.app import TODAY, UPLOAD, chunks, reminders
from telegram_labs.schedule import Schedule, parse_schedule, parse_time
from telegram_labs.storage import Store
from telegram_labs.testing import OfflineTelegram, incoming

TIMETABLE = Path(__file__).resolve().parents[1] / "telegram_labs/data/iu5_32b.txt"
SIMPLE = "Пн | 08:30-10:00 | Математика | 501 | каждую"


def test_real_schedule_and_week_transition():
    schedule = parse_schedule(TIMETABLE.read_text(encoding="utf-8"))
    assert len(schedule.lessons) == 25
    assert schedule.week_on(date(2026, 10, 25)) == "ЗН"
    assert schedule.week_on(date(2026, 10, 26)) == "ЧС"
    assert schedule.week_on(date(2026, 11, 2)) == "ЗН"
    assert [x.start for x in schedule.on(date(2026, 10, 21))] == ["10:10", "12:25", "14:05"]
    assert "Электротехника, лабораторная" in schedule.render_day(date(2026, 10, 28))
    assert "самостоятельной работы" in schedule.render_day(date(2026, 10, 23))
    assert "Занятий по расписанию нет" in schedule.render_day(date(2026, 10, 25))
    assert Schedule.loads(schedule.dumps()) == schedule


@pytest.mark.parametrize("text", [
    "", "Пн | 25:00-26:00 | Тест | 1 | каждую", "Пн | 10:00-09:00 | Тест | 1 | каждую",
    "Пн | 08:30-10:00 | Тест | 1 | ЧС", "Неделя ЧС: 2026-10-27\n" + SIMPLE,
    SIMPLE + "\nПн | 09:00-11:00 | Другой | 1 | каждую",
    "Пн | 08:30-10:00 | Тест | 1 | неизвестно",
])
def test_reject_invalid_import(text):
    with pytest.raises(ValueError):
        parse_schedule(text)


def test_time_and_long_unicode():
    assert parse_time("7:00") == "07:00"
    for bad in ("24:00", "12:60", "07:0", "no"):
        with pytest.raises(ValueError):
            parse_time(bad)
    text = "😀" * 5000
    parts = list(chunks(text))
    assert "".join(parts) == text
    assert all(len(part.encode("utf-16-le")) // 2 < 4096 for part in parts)


def test_store_isolation_restart_and_daily_marker(tmp_path):
    path = tmp_path / "diary.sqlite3"
    db = Store(path)
    schedule = parse_schedule(SIMPLE)
    db.save(1, schedule, "07:00")
    db.save(2, schedule, "09:00")
    current = datetime(2026, 10, 21, 8, tzinfo=ZoneInfo("Europe/Moscow"))
    assert [x["chat_id"] for x in db.due(current)] == [1]
    db.mark_sent(1, current)
    restarted = Store(path)
    assert restarted.due(current) == []
    restarted.save(1, schedule, "07:30")
    assert restarted.due(current) == []
    tomorrow = current.replace(day=22)
    assert [x["chat_id"] for x in restarted.due(tomorrow)] == [1]
    restarted.disable(1)
    assert restarted.due(tomorrow) == []
    restarted.set_reminder(1, "06:30")
    assert len(restarted.due(tomorrow)) == 1
    restarted.delete(1)
    assert restarted.get(1) is None
    assert restarted.get(2) is not None


def test_buttons_import_and_failed_replacement(tmp_path):
    async def scenario():
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "bot.sqlite3", transport)
        async with app:
            for text in ("/start", UPLOAD, SIMPLE, TODAY):
                await app.process_update(incoming(app.bot, text))
            old = app.bot_data["store"].get(42)
            assert old is not None
            assert any("Сохранено занятий: 1" in x["text"] for x in transport.messages)
            await app.process_update(incoming(app.bot, "Пн | сломанное расписание"))
            assert app.bot_data["store"].get(42) == old
            await app.process_update(incoming(app.bot, "/notify 09:15"))
            assert app.bot_data["store"].get(42)["notify_time"] == "09:15"
            await app.process_update(incoming(app.bot, "/off"))
            assert app.bot_data["store"].get(42)["enabled"] == 0
            await app.process_update(incoming(app.bot, "/today", chat_id=7))
            assert len(Schedule.loads(app.bot_data["store"].get(7)["schedule"]).lessons) == 25
            assert app.bot_data["store"].get(42)["schedule"] == old["schedule"]
    asyncio.run(scenario())


def test_daily_send_retry_and_blocked_chat(tmp_path, monkeypatch):
    async def scenario():
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "bot.sqlite3", transport)
        async with app:
            current = datetime(2026, 10, 21, 7, tzinfo=ZoneInfo("Europe/Moscow"))
            monkeypatch.setattr("telegram_labs.app.now", lambda context: current)
            db = app.bot_data["store"]
            db.save(42, parse_schedule(SIMPLE))
            context = SimpleNamespace(bot_data=app.bot_data, bot=app.bot)
            transport.failure = (500, "Internal Server Error")
            await reminders(context)
            assert db.get(42)["last_sent"] is None
            transport.failure = None
            await reminders(context)
            await reminders(context)
            assert len(transport.messages) == 1
            assert db.get(42)["last_sent"] == "2026-10-21"
            db.save(7, parse_schedule(SIMPLE))
            transport.failure = (403, "Forbidden: bot was blocked by the user")
            await reminders(context)
            assert db.get(7)["enabled"] == 0
    asyncio.run(scenario())

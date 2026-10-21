import asyncio
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from telegram.error import TimedOut

from lab_06.main import SAVE, build_application
from telegram_labs.app import reminders
from telegram_labs.schedule import Schedule
from telegram_labs.testing import OfflineTelegram, incoming

MOSCOW = ZoneInfo("Europe/Moscow")


def test_start_connects_timetable_and_daily_0800_without_upload(tmp_path, monkeypatch):
    async def scenario():
        current = datetime(2026, 10, 21, 21, 10, tzinfo=MOSCOW)
        monkeypatch.setattr("telegram_labs.app.now", lambda context: current)
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "diary.sqlite3", transport)
        async with app:
            await app.process_update(incoming(app.bot, "/start", timestamp=int(current.timestamp())))
            row = app.bot_data["store"].get(42)
            assert row["notify_time"] == "08:00" and row["enabled"] == 1
            assert len(Schedule.loads(row["schedule"]).lessons) == 25
            assert "Среда, 21.10.2026 · ЗН" in transport.messages[-1]["text"]
            assert "10:10–11:40 · Электротехника" in transport.messages[-1]["text"]
            before = len(transport.messages)
            await reminders(SimpleNamespace(bot=app.bot, bot_data=app.bot_data))
            assert len(transport.messages) == before  # Нет повторной рассылки сразу после /start.
            await app.process_update(incoming(app.bot, "/off"))
            await app.process_update(incoming(app.bot, "/start"))
            assert app.bot_data["store"].get(42)["enabled"] == 0
    asyncio.run(scenario())


def test_request_uses_sending_date_daily_job_uses_current_date(tmp_path, monkeypatch):
    async def scenario():
        sent = datetime(2026, 10, 21, 23, 59, tzinfo=MOSCOW)
        processed = datetime(2026, 10, 22, 8, 0, tzinfo=MOSCOW)
        monkeypatch.setattr("telegram_labs.app.now", lambda context: processed)
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "diary.sqlite3", transport)
        async with app:
            await app.process_update(incoming(app.bot, "расписание", timestamp=int(sent.timestamp())))
            assert "Среда, 21.10.2026 · ЗН" in transport.messages[-1]["text"]
            await reminders(SimpleNamespace(bot=app.bot, bot_data=app.bot_data))
            assert "Четверг, 22.10.2026 · ЗН" in transport.messages[-1]["text"]
            assert "Иностранный язык" in transport.messages[-1]["text"]
            sent_next = datetime(2026, 10, 26, 10, 0, tzinfo=MOSCOW)
            await app.process_update(incoming(app.bot, "/today", timestamp=int(sent_next.timestamp())))
            assert "Понедельник, 26.10.2026 · ЧС" in transport.messages[-1]["text"]
    asyncio.run(scenario())


def test_800_and_temporary_timeout_do_not_break_confirmation(tmp_path):
    async def scenario():
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "diary.sqlite3", transport)
        async with app:
            await app.process_update(incoming(app.bot, "/upload"))
            await app.process_update(incoming(app.bot, "Ср | 10:10-11:40 | Электротехника | 527к | каждую"))
            before = len(transport.messages)
            transport.send_failures = [TimedOut()]
            await app.process_update(incoming(app.bot, "8:00"))
            assert len(transport.messages) == before + 1
            assert "Шаг 3/3" in transport.messages[-1]["text"]
            assert "08:00" in transport.messages[-1]["text"]
            assert "Не удалось" not in transport.messages[-1]["text"]
            await app.process_update(incoming(app.bot, SAVE))
            assert app.bot_data["store"].get(42)["notify_time"] == "08:00"
    asyncio.run(scenario())

import asyncio

from telegram.ext import ConversationHandler

from lab_06.main import CONFIRM, REMINDER_TIME, SAVE, SCHEDULE, build_application
from telegram_labs.schedule import parse_schedule
from telegram_labs.testing import OfflineTelegram, incoming

SIMPLE = "Пн | 08:30-10:00 | Математика | 501 | каждую"


def test_three_states_and_complete_dialogue(tmp_path):
    async def scenario():
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "diary.sqlite3", transport)
        conversation = app.handlers[0][0]
        assert set(conversation.states) == {SCHEDULE, REMINDER_TIME, CONFIRM}
        async with app:
            db = app.bot_data["store"]
            for text, expected in (("/upload", "Шаг 1/3"), ("ошибка", "Нужно 5 полей"),
                                   (SIMPLE, "Шаг 2/3"), ("25:00", "Часы"), ("07:30", "Шаг 3/3")):
                await app.process_update(incoming(app.bot, text))
                assert expected in "\n".join(x["text"] for x in transport.messages[-3:])
                assert db.get(42) is None
            await app.process_update(incoming(app.bot, "что-то ещё"))
            assert db.get(42) is None
            await app.process_update(incoming(app.bot, SAVE))
            assert db.get(42)["notify_time"] == "07:30"
            assert "draft" not in app.user_data[42]
            await app.process_update(incoming(app.bot, "/today"))
            assert "Пока нет расписания" not in transport.messages[-1]["text"]
    asyncio.run(scenario())


def test_cancel_keeps_previous_schedule_and_users_are_isolated(tmp_path):
    async def scenario():
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "diary.sqlite3", transport)
        async with app:
            db = app.bot_data["store"]
            db.save(42, parse_schedule(SIMPLE), "06:00")
            old = db.get(42)
            await app.process_update(incoming(app.bot, "/upload"))
            await app.process_update(incoming(app.bot, SIMPLE))
            await app.process_update(incoming(app.bot, "/upload", chat_id=7))
            await app.process_update(incoming(app.bot, "08:00"))
            await app.process_update(incoming(app.bot, "/cancel"))
            assert db.get(42) == old
            assert "draft" not in app.user_data[42]
            await app.process_update(incoming(app.bot, SIMPLE, chat_id=7))
            await app.process_update(incoming(app.bot, "09:00", chat_id=7))
            await app.process_update(incoming(app.bot, SAVE, chat_id=7))
            assert db.get(7)["notify_time"] == "09:00"
            assert db.get(42) == old
    asyncio.run(scenario())


def test_txt_upload_and_restart_command(tmp_path):
    async def scenario():
        transport = OfflineTelegram()
        app = build_application("123456789:offline_test", tmp_path / "diary.sqlite3", transport)
        async with app:
            await app.process_update(incoming(app.bot, "/upload"))
            await app.process_update(incoming(app.bot, document={"file_name": "photo.pdf", "file_size": 500}))
            assert "Фото и PDF" in transport.messages[-1]["text"]
            await app.process_update(incoming(app.bot, document={"file_name": "big.txt", "file_size": 100001}))
            assert "100 КБ" in transport.messages[-1]["text"]
            transport.file_content = b"\xff\xfe"
            await app.process_update(incoming(app.bot, document={"file_name": "bad.txt", "file_size": 2}))
            assert "UTF-8" in transport.messages[-1]["text"]
            transport.file_content = SIMPLE.encode("utf-8-sig")
            await app.process_update(incoming(app.bot, document={"file_name": "schedule.txt", "file_size": len(transport.file_content)}))
            assert "Шаг 2/3" in transport.messages[-1]["text"]
            await app.process_update(incoming(app.bot, "/start"))
            assert "draft" not in app.user_data[42]
            await app.process_update(incoming(app.bot, "07:00"))
            assert "Для загрузки" in transport.messages[-1]["text"]
    asyncio.run(scenario())

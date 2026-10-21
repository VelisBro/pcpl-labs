"""SQLite: отдельное расписание, время рассылки и отметка отправки для каждого чата."""
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
import sqlite3

from .schedule import Schedule, parse_time


class Store:
    def __init__(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS diaries (
                chat_id INTEGER PRIMARY KEY, schedule TEXT NOT NULL,
                notify_time TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
                last_sent TEXT)""")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def get(self, chat_id: int):
        with self.connect() as db:
            row = db.execute("SELECT * FROM diaries WHERE chat_id=?", (chat_id,)).fetchone()
            return dict(row) if row else None

    def save(self, chat_id: int, schedule: Schedule, notify_time: str = "07:00"):
        notify_time = parse_time(notify_time)
        with self.connect() as db:
            db.execute("""INSERT INTO diaries (chat_id, schedule, notify_time) VALUES (?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET schedule=excluded.schedule,
                notify_time=excluded.notify_time, enabled=1""",
                       (chat_id, schedule.dumps(), notify_time))

    def set_reminder(self, chat_id: int, value: str):
        value = parse_time(value)
        with self.connect() as db:
            db.execute("UPDATE diaries SET notify_time=?, enabled=1 WHERE chat_id=?", (value, chat_id))

    def disable(self, chat_id: int):
        with self.connect() as db:
            db.execute("UPDATE diaries SET enabled=0 WHERE chat_id=?", (chat_id,))

    def delete(self, chat_id: int):
        with self.connect() as db:
            db.execute("DELETE FROM diaries WHERE chat_id=?", (chat_id,))

    def due(self, now: datetime):
        with self.connect() as db:
            return [dict(x) for x in db.execute("""SELECT * FROM diaries WHERE enabled=1
                AND notify_time <= ? AND (last_sent IS NULL OR last_sent != ?)""",
                (now.strftime("%H:%M"), now.date().isoformat()))]

    def mark_sent(self, chat_id: int, now: datetime):
        with self.connect() as db:
            db.execute("UPDATE diaries SET last_sent=? WHERE chat_id=?", (now.date().isoformat(), chat_id))

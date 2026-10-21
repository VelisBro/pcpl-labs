"""Разбор текстового расписания и чередование числителя/знаменателя."""
from dataclasses import asdict, dataclass
from datetime import date, timedelta
import json
import re

DAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
DAY_NAMES = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье")
WEEKS = {"каждую": "all", "чс": "ЧС", "зн": "ЗН"}


def parse_time(value: str) -> str:
    """Проверить время, привести 7:00 к 07:00."""
    if not re.fullmatch(r"\d{1,2}:\d{2}", value.strip()):
        raise ValueError("Время должно быть в формате ЧЧ:ММ, например 07:00.")
    hour, minute = map(int, value.split(":"))
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("Часы: 00–23, минуты: 00–59.")
    return f"{hour:02}:{minute:02}"


@dataclass(frozen=True)
class Lesson:
    day: int
    start: str
    end: str
    subject: str
    room: str
    week: str


@dataclass(frozen=True)
class Schedule:
    lessons: tuple[Lesson, ...]
    numerator_monday: date | None = None
    notes: tuple[tuple[int, str], ...] = ()

    def week_on(self, day: date) -> str:
        if self.numerator_monday is None:
            return "каждую неделю"
        # Целочисленное деление работает и для дат до опорного понедельника.
        weeks = (day - self.numerator_monday).days // 7
        return "ЧС" if weeks % 2 == 0 else "ЗН"

    def on(self, day: date) -> list[Lesson]:
        return sorted((lesson for lesson in self.lessons
                       if lesson.day == day.weekday()
                       and lesson.week in ("all", self.week_on(day))), key=lambda x: x.start)

    def render_day(self, day: date) -> str:
        lines = [f"{DAY_NAMES[day.weekday()]}, {day:%d.%m.%Y} · {self.week_on(day)}"]
        lessons = self.on(day)
        for lesson in lessons:
            lines.append(f"\n{lesson.start}–{lesson.end} · {lesson.subject}\n📍 {lesson.room}")
        if not lessons:
            lines.append("\nЗанятий по расписанию нет.")
        for weekday, note in self.notes:
            if weekday == day.weekday():
                lines.append(f"\n📝 {note}")
        return "\n".join(lines)

    def render_week(self, day: date) -> str:
        monday = day - timedelta(days=day.weekday())
        return "\n\n".join(self.render_day(monday + timedelta(days=i)) for i in range(7))

    def dumps(self) -> str:
        return json.dumps({"lessons": [asdict(x) for x in self.lessons],
                           "numerator_monday": self.numerator_monday.isoformat() if self.numerator_monday else None,
                           "notes": self.notes}, ensure_ascii=False)

    @classmethod
    def loads(cls, raw: str) -> "Schedule":
        data = json.loads(raw)
        return cls(tuple(Lesson(**x) for x in data["lessons"]),
                   date.fromisoformat(data["numerator_monday"]) if data["numerator_monday"] else None,
                   tuple(tuple(x) for x in data.get("notes", [])))


def parse_schedule(text: str) -> Schedule:
    """Формат: Пн | 08:30-10:00 | Предмет | Аудитория | ЧС/ЗН/каждую."""
    if len(text) > 40000:
        raise ValueError("Расписание слишком большое: максимум 40 000 символов.")
    lessons, notes = [], []
    anchor = None
    for number, raw in enumerate(text.lstrip("\ufeff").splitlines(), 1):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        try:
            if raw.lower().startswith("неделя чс:"):
                if anchor is not None:
                    raise ValueError("Укажи только одну опорную неделю ЧС.")
                anchor = date.fromisoformat(raw.split(":", 1)[1].strip())
                if anchor.weekday() != 0:
                    raise ValueError("Дата недели ЧС должна приходиться на понедельник.")
                continue
            parts = [x.strip() for x in raw.split("|")]
            if len(parts) == 3 and parts[1].lower() == "заметка":
                weekday = DAYS.index(parts[0].capitalize())
                if not parts[2] or len(parts[2]) > 300:
                    raise ValueError("Заметка должна содержать от 1 до 300 символов.")
                notes.append((weekday, parts[2]))
                continue
            if len(parts) != 5:
                raise ValueError("Нужно 5 полей: день | время | предмет | аудитория | неделя.")
            weekday = DAYS.index(parts[0].capitalize())
            times = re.split(r"\s*[-–—]\s*", parts[1])
            if len(times) != 2:
                raise ValueError("Интервал времени: 08:30-10:00.")
            start, end = map(parse_time, times)
            if start >= end:
                raise ValueError("Начало занятия должно быть раньше окончания.")
            if not parts[2] or len(parts[2]) > 160 or not parts[3] or len(parts[3]) > 100:
                raise ValueError("Укажи предмет (до 160 символов) и место (до 100 символов).")
            if parts[4].lower() not in WEEKS:
                raise ValueError("Неделя: ЧС, ЗН или каждую.")
            lesson = Lesson(weekday, start, end, parts[2], parts[3], WEEKS[parts[4].lower()])
            for old in lessons:
                same_week = old.week == lesson.week or "all" in (old.week, lesson.week)
                if old.day == lesson.day and same_week and old.start < lesson.end and lesson.start < old.end:
                    raise ValueError("Занятия пересекаются по времени; проверь строки расписания.")
            lessons.append(lesson)
        except ValueError as error:
            raise ValueError(f"Строка {number}: {error}") from None
        if len(lessons) > 100:
            raise ValueError("Максимум 100 занятий.")
    if not lessons:
        raise ValueError("Не найдено занятий. Пришли расписание в указанном формате.")
    if anchor is None and any(x.week != "all" for x in lessons):
        raise ValueError("Для ЧС/ЗН добавь строку «Неделя ЧС: ГГГГ-ММ-ДД» с понедельником числителя.")
    return Schedule(tuple(lessons), anchor, tuple(notes))

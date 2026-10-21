"""Общие команды, кнопки, загрузка TXT и ежедневная рассылка."""
from datetime import datetime, timedelta
from io import BytesIO
import logging
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import BotCommand, ReplyKeyboardMarkup, Update
from telegram.error import Conflict, Forbidden, InvalidToken, NetworkError, TelegramError
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .schedule import Schedule, parse_time
from .storage import Store

ROOT = Path(__file__).resolve().parents[1]
TODAY, TOMORROW, WEEK = "📅 Сегодня", "➡️ Завтра", "🗓 Неделя"
UPLOAD, SETTINGS, TEMPLATE = "📥 Загрузить расписание", "⚙️ Уведомления", "📄 Файл расписания"
MENU = ReplyKeyboardMarkup([[TODAY, TOMORROW, WEEK], [UPLOAD], [SETTINGS, TEMPLATE]], resize_keyboard=True)
PRIVATE_TEXT = filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND
SCHEDULE_INPUT = filters.ChatType.PRIVATE & (filters.TEXT | filters.Document.ALL) & ~filters.COMMAND
FORMAT = (
    "Пришли расписание одним сообщением или файлом .txt в UTF-8.\n"
    "Каждое занятие — отдельная строка:\n"
    "Пн | 08:30-10:00 | Математика, лекция | 501 | каждую\n\n"
    "Для чередующихся недель используй ЧС или ЗН вместо «каждую» и добавь, например:\n"
    "Неделя ЧС: 2026-10-26\n"
    "Это дата понедельника известной недели ЧС.\n"
    "Заметка на день: Пт | заметка | День самостоятельной работы\n\n"
    "Кнопка «Файл расписания» или /template выдаёт подготовленное расписание ИУ5-32Б по твоим скриншотам."
)
LOG = logging.getLogger(__name__)


def chunks(text: str):
    # 1800 Unicode-символов не превышают 3600 UTF-16 единиц даже с emoji.
    while text:
        split = text.rfind("\n", 0, 1800) if len(text) > 1800 else len(text)
        if split <= 0:
            split = min(1800, len(text))
        yield text[:split]
        text = text[split:].lstrip("\n")


async def reply(update: Update, text: str, markup=MENU):
    for part in chunks(text):
        await update.effective_message.reply_text(part, reply_markup=markup)


async def read_input(update: Update) -> str:
    message = update.effective_message
    if message.document:
        document = message.document
        if not (document.file_name or "").lower().endswith(".txt"):
            raise ValueError("Пришли текст или файл .txt. Фото и PDF автоматически не распознаются.")
        if document.file_size is None or document.file_size > 100_000:
            raise ValueError("Максимальный размер файла — 100 КБ.")
        file = await document.get_file()
        content = await file.download_as_bytearray()
        if len(content) > 100_000:
            raise ValueError("Максимальный размер файла — 100 КБ.")
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ValueError("Сохрани файл в кодировке UTF-8 и отправь ещё раз.") from None
    return message.text or ""


def store(context: ContextTypes.DEFAULT_TYPE) -> Store:
    return context.bot_data["store"]


def now(context: ContextTypes.DEFAULT_TYPE) -> datetime:
    return datetime.now(context.bot_data["timezone"])


def clear_draft(context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("draft", None)
    context.user_data.pop("draft_time", None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft(context)
    row = store(context).get(update.effective_chat.id)
    status = "Расписание сохранено." if row else "Сначала загрузи расписание."
    await reply(update, f"Привет! Я учебный ежедневник. Лабораторная №{context.bot_data['lab']}.\n"
                f"{status}\n\nПокажу занятия на сегодня, завтра и неделю. "
                "После загрузки могу присылать их каждый день в выбранное время.\n"
                "Все даты и время: " + str(context.bot_data["timezone"]) + ".\n"
                "/help — формат загрузки; /cancel — отмена ввода.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply(update, FORMAT + "\n\n/today /tomorrow /week — занятия\n"
                "/notify 07:00 — включить рассылку или изменить время\n"
                "/off — выключить рассылку\n/delete — удалить свои данные")


async def template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = (ROOT / "telegram_labs/data/iu5_32b.txt").read_bytes()
    await update.effective_message.reply_document(
        document=BytesIO(data), filename="iu5_32b.txt",
        caption="Расписание ИУ5-32Б: проверь аудитории и подгруппу. Для загрузки отправь этот файл боту.")


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    row = store(context).get(update.effective_chat.id)
    if row is None:
        await reply(update, "Пока нет расписания. Нажми «Загрузить расписание».")
        return
    schedule = Schedule.loads(row["schedule"])
    day = now(context).date()
    if mode == "tomorrow":
        day += timedelta(days=1)
    text = schedule.render_week(day) if mode == "week" else schedule.render_day(day)
    await reply(update, text)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show(update, context, "today")


async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show(update, context, "tomorrow")


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show(update, context, "week")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    row = store(context).get(update.effective_chat.id)
    if row is None:
        await reply(update, "Сначала загрузи расписание.")
        return
    state = f"каждый день в {row['notify_time']}" if row["enabled"] else "выключены"
    await reply(update, f"Уведомления: {state}. Часовой пояс: {context.bot_data['timezone']}.\n"
                "Изменить время: /notify 07:00\nВыключить: /off\n"
                "Программа должна работать постоянно. Если включить её после выбранного времени, "
                "она пришлёт расписание за текущий день в течение минуты.")


async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not store(context).get(update.effective_chat.id):
        await reply(update, "Сначала загрузи расписание.")
        return
    try:
        if len(context.args) != 1:
            raise ValueError("Пример команды: /notify 07:00")
        value = parse_time(context.args[0])
    except ValueError as error:
        await reply(update, str(error))
        return
    store(context).set_reminder(update.effective_chat.id, value)
    await reply(update, f"Буду присылать занятия ежедневно в {value} ({context.bot_data['timezone']}).")


async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store(context).disable(update.effective_chat.id)
    await reply(update, "Ежедневная отправка выключена. Включить снова: /notify 07:00")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args != ["confirm"]:
        await reply(update, "Чтобы удалить своё расписание и отключить рассылку, отправь /delete confirm")
        return
    store(context).delete(update.effective_chat.id)
    clear_draft(context)
    await reply(update, "Твоё расписание удалено, рассылка отключена.")


async def route_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    action = {TODAY: today, TOMORROW: tomorrow, WEEK: week,
              SETTINGS: settings, TEMPLATE: template}.get(update.effective_message.text)
    if action:
        await action(update, context)
        return True
    return False


async def reminders(context: ContextTypes.DEFAULT_TYPE):
    current = now(context)
    database = store(context)
    for row in database.due(current):
        try:
            text = "☀️ Занятия на сегодня\n\n" + Schedule.loads(row["schedule"]).render_day(current.date())
            for part in chunks(text):
                await context.bot.send_message(chat_id=row["chat_id"], text=part)
            # Запись после успешной отправки не допускает обычных повторов после перезапуска.
            database.mark_sent(row["chat_id"], current)
        except Forbidden:
            database.disable(row["chat_id"])
        except TelegramError as error:
            # Не логируем URL запроса: в URL Telegram API содержится токен.
            LOG.warning("Рассылка отложена: %s", type(error).__name__)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Открыть ежедневник"), BotCommand("upload", "Загрузить расписание"),
        BotCommand("today", "Занятия сегодня"), BotCommand("tomorrow", "Занятия завтра"),
        BotCommand("week", "Текущая неделя"), BotCommand("notify", "Настроить ежедневную отправку"),
        BotCommand("off", "Отключить отправку"), BotCommand("template", "Файл расписания ИУ5-32Б"),
        BotCommand("help", "Помощь"), BotCommand("cancel", "Отменить ввод")])


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    LOG.error("Ошибка обработки: %s", type(context.error).__name__)
    if isinstance(update, Update) and update.effective_message:
        try:
            await reply(update, "Не удалось обработать запрос. Попробуй ещё раз или отправь /start.")
        except TelegramError:
            pass


def create_base(lab: int, token: str | None = None, db_path: Path | None = None, request=None) -> Application:
    load_dotenv(ROOT / "telegram_labs/.env")
    token = token or os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "PASTE_NEW_TOKEN_HERE":
        raise ValueError("Укажи новый BOT_TOKEN в telegram_labs/.env (пример: .env.example).")
    timezone = ZoneInfo(os.getenv("BOT_TIMEZONE", "Europe/Moscow"))
    builder = Application.builder().token(token).concurrent_updates(False).post_init(post_init)
    if request is not None:
        builder = builder.request(request).get_updates_request(request)
    application = builder.build()
    application.bot_data.update(store=Store(db_path or ROOT / f"lab_{lab:02}/data/diary.sqlite3"),
                                timezone=timezone, lab=lab)
    application.job_queue.run_repeating(reminders, interval=30, first=1,
                                         job_kwargs={"max_instances": 1, "coalesce": True})
    application.add_error_handler(error_handler)
    return application


def add_common_handlers(application: Application, include_start=True):
    commands = {"help": help_command, "today": today, "tomorrow": tomorrow, "week": week,
                "notify": notify, "off": off, "delete": delete, "template": template}
    if include_start:
        commands["start"] = start
    for name, callback in commands.items():
        application.add_handler(CommandHandler(name, callback, filters=filters.ChatType.PRIVATE))


def run(factory):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    for name in ("httpx", "httpcore", "telegram", "apscheduler"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    try:
        application = factory()
    except (ValueError, KeyError) as error:
        raise SystemExit(str(error)) from None
    print("Учебный ежедневник запущен. Остановка: Ctrl+C.")
    try:
        application.run_polling(allowed_updates=["message"], drop_pending_updates=False)
    except InvalidToken:
        raise SystemExit("Telegram отклонил токен. Повторный ввод: python telegram_labs/launch.py --configure") from None
    except Conflict:
        raise SystemExit("Этот бот уже запущен в другом процессе. Останови второй экземпляр и повтори запуск.") from None
    except NetworkError:
        raise SystemExit("Не удалось подключиться к Telegram. Проверь интернет и повтори запуск.") from None
    except TelegramError as error:
        raise SystemExit(f"Ошибка Telegram: {type(error).__name__}. Проверь настройки и повтори запуск.") from None

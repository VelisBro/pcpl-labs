"""ЛР 5: простой Telegram-бот с кнопками и загрузкой расписания."""
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from telegram_labs.app import (
    FORMAT, SCHEDULE_INPUT, UPLOAD, add_common_handlers, create_base, read_input,
    reply, route_buttons, run, store,
)
from telegram_labs.schedule import parse_schedule


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply(update, FORMAT + "\n\nПосле загрузки рассылка включится на 07:00. Изменить: /notify 08:00")


async def receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await route_buttons(update, context):
        return
    if update.effective_message.text == UPLOAD:
        await upload(update, context)
        return
    try:
        schedule = parse_schedule(await read_input(update))
    except ValueError as error:
        await reply(update, str(error) + "\n\nФормат: /help")
        return
    old = store(context).get(update.effective_chat.id)
    reminder = old["notify_time"] if old else "07:00"
    store(context).save(update.effective_chat.id, schedule, reminder)
    await reply(update, f"Сохранено занятий: {len(schedule.lessons)}.\n"
                f"Ежедневная отправка: {reminder} ({context.bot_data['timezone']}).\n"
                "Нажми «Сегодня», «Завтра» или «Неделя».")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply(update, "Можно пользоваться меню. Сохранённое расписание не менялось.")


def build_application(token=None, db_path=None, request=None):
    application = create_base(5, token, db_path, request)
    add_common_handlers(application)
    application.add_handler(CommandHandler("upload", upload, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("cancel", cancel, filters=filters.ChatType.PRIVATE))
    application.add_handler(MessageHandler(SCHEDULE_INPUT, receive))
    return application


if __name__ == "__main__":
    run(build_application)

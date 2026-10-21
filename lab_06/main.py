"""ЛР 6: конечный автомат ровно из трёх состояний импорта расписания."""
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from telegram_labs.app import (
    FORMAT, PRIVATE_TEXT, SCHEDULE_INPUT, UPLOAD, add_common_handlers, clear_draft,
    create_base, delete, read_input, reply, request_day, route_buttons, run, start, store,
)
from telegram_labs.schedule import parse_schedule, parse_time

# Вне диалога работает главное меню; END — завершение, а не четвёртое состояние.
SCHEDULE, REMINDER_TIME, CONFIRM = range(3)
SAVE, CANCEL = "✅ Сохранить", "❌ Отмена"
CONFIRM_KEYS = ReplyKeyboardMarkup([[SAVE, CANCEL]], resize_keyboard=True, one_time_keyboard=True)


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft(context)
    await reply(update, "Шаг 1/3 — расписание\n\n" + FORMAT + "\n\nОтмена: /cancel",
                ReplyKeyboardRemove())
    return SCHEDULE


async def receive_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        schedule = parse_schedule(await read_input(update))
    except ValueError as error:
        await reply(update, str(error) + "\nОтправь расписание ещё раз или /cancel.", ReplyKeyboardRemove())
        return SCHEDULE
    context.user_data["draft"] = schedule
    await reply(update, f"Шаг 2/3 — время уведомления\n\nПрочитано занятий: {len(schedule.lessons)}.\n"
                f"Во сколько присылать занятия? Введи ЧЧ:ММ, например 07:00.\n"
                f"Часовой пояс: {context.bot_data['timezone']}.\nОтмена: /cancel", ReplyKeyboardRemove())
    return REMINDER_TIME


async def receive_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = parse_time(update.effective_message.text)
    except ValueError as error:
        await reply(update, str(error), ReplyKeyboardRemove())
        return REMINDER_TIME
    context.user_data["draft_time"] = value
    schedule = context.user_data["draft"]
    await reply(update, f"Шаг 3/3 — подтверждение\n\nЗанятий в расписании: {len(schedule.lessons)}.\n"
                f"Ежедневная отправка: {value} ({context.bot_data['timezone']}).\n\n"
                + schedule.render_day(request_day(update, context))
                + "\n\nЭто пример дня. Полная неделя доступна после сохранения.\n"
                "Нажми «Сохранить» или «Отмена».", CONFIRM_KEYS)
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.effective_message.text
    if answer == CANCEL:
        return await cancel(update, context)
    if answer != SAVE:
        await reply(update, "Выбери «Сохранить» или «Отмена».", CONFIRM_KEYS)
        return CONFIRM
    # До этого места изменения существуют только в черновике конкретного пользователя.
    store(context).save(update.effective_chat.id, context.user_data["draft"], context.user_data["draft_time"])
    clear_draft(context)
    await reply(update, "Расписание сохранено, ежедневная отправка включена.\n"
                "Управление: «Сегодня», «Завтра», «Неделя», «Уведомления».")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_draft(context)
    await reply(update, "Ввод отменён. Сохранённое расписание не менялось.")
    return ConversationHandler.END


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
    return ConversationHandler.END


async def unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = CONFIRM_KEYS if "draft_time" in context.user_data else ReplyKeyboardRemove()
    await reply(update, "На этом шаге нужен текст. Для отмены отправь /cancel.", markup)


async def delete_and_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete(update, context)
    if context.args == ["confirm"]:
        return ConversationHandler.END


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await route_buttons(update, context):
        return
    await reply(update, "Для загрузки нажми «Загрузить расписание» или отправь /upload, затем пришли текст или TXT.")


def build_application(token=None, db_path=None, request=None):
    application = create_base(6, token, db_path, request)
    conversation = ConversationHandler(
        entry_points=[CommandHandler("upload", begin, filters=filters.ChatType.PRIVATE),
                      MessageHandler(PRIVATE_TEXT & filters.Regex("^" + re.escape(UPLOAD) + "$"), begin)],
        states={
            SCHEDULE: [MessageHandler(SCHEDULE_INPUT, receive_schedule)],
            REMINDER_TIME: [MessageHandler(PRIVATE_TEXT, receive_time)],
            CONFIRM: [MessageHandler(PRIVATE_TEXT, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel, filters=filters.ChatType.PRIVATE),
                   CommandHandler("start", restart, filters=filters.ChatType.PRIVATE),
                   CommandHandler("delete", delete_and_end, filters=filters.ChatType.PRIVATE),
                   MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, unsupported)],
        allow_reentry=True,
    )
    application.add_handler(conversation)
    add_common_handlers(application)
    application.add_handler(CommandHandler("cancel", cancel, filters=filters.ChatType.PRIVATE))
    application.add_handler(MessageHandler(SCHEDULE_INPUT, menu))
    return application


if __name__ == "__main__":
    run(build_application)

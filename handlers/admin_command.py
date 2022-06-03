import re
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database.user.models import User, Team

SELECTING_ACTION, ADD_TEAM, EDIT_TEAM, \
    DELETE_TEAM, ENTERING_TEAM = map(chr, range(5))

ADD_POINT, EDIT_POINT, DELETE_POINT = map(chr, range(5, 8))

SHOW_ALL_USERS = map(chr, range(8, 9))

STOPPING = map(chr, range(9, 10))

END = ConversationHandler.END


async def admin(update: Update,
                context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    user = update.message.from_user.id
    admin_status = await User.get_or_none(
        telegram_id=user
    ).values('is_admin')

    buttons = [
        [
            InlineKeyboardButton("Добавить сторону",
                                 callback_data=str(ADD_TEAM)),
            InlineKeyboardButton("Ред. сторону",
                                 callback_data=str(EDIT_TEAM)),
            InlineKeyboardButton("Удалить сторону",
                                 callback_data=str(DELETE_TEAM))
        ],
        [
            InlineKeyboardButton("Добавить точку",
                                 callback_data=str(ADD_POINT)),
            InlineKeyboardButton("Ред. точку",
                                 callback_data=str(EDIT_POINT)),
            InlineKeyboardButton("Удалить точку",
                                 callback_data=str(DELETE_POINT))
        ],
        [
            InlineKeyboardButton("Показать всех пользователей",
                                 callback_data=str(SHOW_ALL_USERS)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        if admin_status['is_admin']:
            await update.message.reply_text(
                text='Выбери один из пунктов меню.\n\n'
                     'Для завершения работы с админ меню '
                     'введи команду /stop',
                reply_markup=keyboard
            )

            return SELECTING_ACTION

        else:
            await update.message.reply_text(
                text='У тебя нет админских прав ¯\_(ツ)_/¯'
            )

            return END

    except TypeError:
        await update.message.reply_text(
            text='Без понятия кто ты, пройди регистрацию, '
                 'введя команду /callsign'
        )

        return END


async def adding_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        ENTERING_TEAM:
    text = 'Введи название стороны. Например: желтые.\n\n' \
           'Помни, что название должно быть уникальным.\n' \
           'Команда /stop отменит создание сотороны.'

    query = update.callback_query
    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

    return ENTERING_TEAM


async def commit_team(update: Update,
                      context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:
    text = update.message.text
    text = re.sub(r'[.\W.\d]', '', text)
    text = ''.join(filter(lambda a: a in string.ascii_letters, text))
    text = text.lower()

    await Team.get_or_create(title=text)
    await update.message.reply_text(
        f'{text.capitalize()}, принято и записано в базу данных.'
    )

    return SELECTING_ACTION


async def stop_admin_handler(update: Update,
                             context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    text = 'Выполнение админских команд остановлено.'
    await update.message.reply_text(text=text)

    return END


async def end(update: Update,
              context: CallbackContext.DEFAULT_TYPE) -> END:
    await update.callback_query.answer()

    text = 'Выполнение админских команд остановлено.'
    await update.callback_query.edit_message_text(text=text)

    return END

import re
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from database.user.models import User, Team

SELECTING_ACTION, ADD_TEAM, EDIT_TEAM, DELETE_TEAM, ENTERING_TEAM = map(chr, range(5))

STOPPING = map(chr, range(5, 6))

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
            InlineKeyboardButton("Add team",
                                 callback_data=str(ADD_TEAM)),
            InlineKeyboardButton("Edit team",
                                 callback_data=str(EDIT_TEAM)),
            InlineKeyboardButton("Del team",
                                 callback_data=str(DELETE_TEAM))
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        if admin_status['is_admin']:
            await update.message.reply_text(
                text='Выбери один из пунктов меню:\n\n'
                     'Для завершения работы с админ меню '
                     'введи команду /stop',
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                text='У тебя нет админских прав ¯\_(ツ)_/¯'
            )
    except TypeError:
        await update.message.reply_text(
            text='Без понятия кто ты, пройди регистрацию, '
                 'введя команду /callsign'
        )

    return SELECTING_ACTION


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


async def get_teams() -> list:
    teams = await Team.all().values('title')

    list_of_teams = [team.get('title') for team in teams]

    return list_of_teams


async def stop(update: Update,
               context: CallbackContext.DEFAULT_TYPE) -> \
        SELECTING_ACTION:

    text = 'Выполнение админских команд остановлено.'
    await update.message.reply_text(text=text)

    return END


async def end(update: Update,
              context: CallbackContext.DEFAULT_TYPE) -> END:

    await update.callback_query.answer()

    text = 'Выполнение админских команд остановлено.'
    await update.callback_query.edit_message_text(text=text)

    return END

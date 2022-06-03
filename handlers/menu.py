import re
import string

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from tortoise.exceptions import IntegrityError, ValidationError, DoesNotExist

from settings.settings import CREATORS_ID

from database.user.models import User

from database.db_functions import get_teams, update_players_team

CREATE_OR_UPDATE_CALLSIGN, CHOOSING_TEAM_ACTION = map(chr, range(2))

END = ConversationHandler.END


async def start(update: Update,
                context: CallbackContext.DEFAULT_TYPE) -> None:
    user = update.message.from_user.id

    if user == int(CREATORS_ID):
        await User.get_or_create(telegram_id=user,
                                 is_member=True,
                                 is_admin=True)
    else:
        await User.get_or_create(telegram_id=user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Тут приветственное сообщение'
    )


async def callsign(update: Update,
                   context: CallbackContext.DEFAULT_TYPE) -> \
        CREATE_OR_UPDATE_CALLSIGN:
    user = update.message.from_user.id

    if user == int(CREATORS_ID):
        await User.get_or_create(telegram_id=user,
                                 is_member=True,
                                 is_admin=True)
    else:
        await User.get_or_create(telegram_id=user)

    await update.message.reply_text(
        'Введи свой позывной в текстовом поле и нажми отправить.\n\n'
        'Позывной должен быть уникальным и на латинице, поэтому, если '
        'он уже занят, то я тебя уведмлю об этом. Так же в позывном нельзя '
        'использовать спец. символы, я их просто удалю.\n\n'
        'Для отмены регистрации позывного напиши /cancel в чат.'
    )

    return CREATE_OR_UPDATE_CALLSIGN


async def commit_callsign(update: Update,
                          context: CallbackContext.DEFAULT_TYPE) -> END:
    user = update.message.from_user.id
    text = update.message.text
    text = re.sub(r'[.\W.\d]', '', text)
    text = ''.join(filter(lambda a: a in string.ascii_letters, text))

    try:
        await User.filter(telegram_id=user).update(callsign=text.lower())
        await update.message.reply_text(
            f'{text.capitalize()} - принятно, твой позывной успешно обновлен!'
        )

        return END

    except IntegrityError:
        await update.message.reply_text(
            'Ошибка, такой позывной уже занят или написан кириллицей, а надо латиницей. '
            'Попробуй еще раз.\n\n'
            'Напоминаю, если хочешь отменить регистрацию позывного, '
            'напиши /cancel в чат.'
        )
    except ValidationError:
        await update.message.reply_text(
            'Не особо это на позывной похоже, если честно.\n\n'
            f'Давай-ка, {update.message.from_user.name}, '
            f'все по новой.'
        )


async def stop_callsign_handler(update: Update,
                                context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    await update.message.reply_text(
        'Обновление позывного отменено.'
    )

    return END


async def team(update: Update,
               context: CallbackContext.DEFAULT_TYPE) -> \
        CHOOSING_TEAM_ACTION:
    buttons = []
    teams = await get_teams()

    for team_title in teams:
        buttons.append(
            [
                InlineKeyboardButton(team_title.capitalize(),
                                     callback_data=str(
                                         f'TEAM_COLOR_{team_title.upper()}')
                                     )
            ]
        )

    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        text='Выбери сторону из предложенных ниже:',
        reply_markup=keyboard
    )

    return CHOOSING_TEAM_ACTION


async def choose_the_team(update: Update,
                          context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    await update.callback_query.answer()

    callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
    callback_data = callback_data.lower()

    try:
        await update_players_team(
            int(update.callback_query.from_user.id), str(callback_data)
        )

        text = f'Выбрана сторона: {callback_data.capitalize()}'
        await update.callback_query.edit_message_text(text=text)

    except DoesNotExist:
        text = 'Что-то пошло не так. Скорее всего ты не ' \
               'зарегистрирован(а). Можешь сделать это при ' \
               'помощи команды /callsign'
        await update.callback_query.edit_message_text(text=text)

    return END


async def stop_team_handler(update: Update,
                            context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    text = 'Выбор стороны прекращен. Если нужно выбрать сторону, ' \
           'повторно введи /team в чат.'
    await update.message.reply_text(text=text)

    return END

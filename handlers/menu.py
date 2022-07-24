import re
import string
from typing import NoReturn

from telegram import Update
from telegram.error import BadRequest

from telegram.ext import (
    CallbackContext,
    ApplicationHandlerStop,
)

from telegram.constants import ParseMode

from tortoise.exceptions import (
    IntegrityError,
    ValidationError,
    DoesNotExist,
)

from transliterate import translit

from settings.settings import CREATORS_ID, CREATORS_USERNAME

from keyboards.keyboards import (
    END,
    teams_keyboard,
    point_activation_keyboard,
)

from database.user.models import User
from database.db_functions import (
    get_teams,
    update_players_team,
    get_user_callsign,
    update_users_in_game,
)

CREATE_OR_UPDATE_CALLSIGN, CHOOSING_TEAM_ACTION = map(chr, range(2))


async def start(update: Update,
                context: CallbackContext.DEFAULT_TYPE) -> NoReturn:
    """
    Initializing the bot and sending a welcome message to the user.
    """

    user = update.message.from_user.id

    if user == int(CREATORS_ID):
        await User.get_or_create(telegram_id=user,
                                 is_admin=True)
    else:
        await User.get_or_create(telegram_id=user)
    greetings_text = f'Ну здорова, {update.message.from_user.name}.\n\n' \
                     f'Это тренировочный бот, который завязан на ' \
                     f'работе с геолокацией. На данный момент он ' \
                     f'умеет активировать точки и... выводить их ' \
                     f'из игры, оповещая при этом всех игроков на ' \
                     f'полигоне. Для начала работы с ботом необходимо ' \
                     f'пройти простую регистрацию.\n\n' \
                     f'<b>Доступные пользовательские команды:</b>\n' \
                     f'/callsign - регистрация своего позывного в боте\n' \
                     f'/team - выбор игровой стороны\n\n' \
                     f'<i>Создатель чат-бота: @vmstr8</i>'

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=greetings_text,
        parse_mode=ParseMode.HTML,
        reply_markup=point_activation_keyboard()
    )


async def callsign(update: Update,
                   context: CallbackContext.DEFAULT_TYPE) -> \
        CREATE_OR_UPDATE_CALLSIGN:
    """
    The beginning of user registration in the chatbot.
    """

    user = update.message.from_user.id

    if user == int(CREATORS_ID):
        await User.get_or_create(telegram_id=user,
                                 is_admin=True)
    else:
        await User.get_or_create(telegram_id=user)

    text = 'Введи свой позывной в текстовом поле и нажми отправить.\n\n' \
           'Позывной должен быть уникальным и на латинице, поэтому, если ' \
           'он уже занят, то я тебя уведомлю об этом. ' \
           'Так же в позывном нельзя использовать спец. символы, ' \
           'я их просто удалю.\n\n' \
           'Для отмены регистрации позывного напиши /cancel в чат.'
    save_data = await update.message.reply_text(text=text)

    context.user_data['callsign_message_id'] = int(save_data.message_id)

    return CREATE_OR_UPDATE_CALLSIGN


async def commit_callsign(update: Update,
                          context: CallbackContext.DEFAULT_TYPE) -> END:
    """
    Confirmation of the callsign that the user entered.
    If the callsign already used by another player or an
    unexpected error has occurred, the bot will prompt you
    to enter the callsign again.
    """

    user = update.message.from_user.id

    users_text = update.message.text
    users_text = translit(users_text, language_code='ru', reversed=True)
    users_text = ''.join(
        filter(
            lambda letters:
            letters in string.ascii_letters or letters in string.digits,
            users_text
        )
    )

    try:
        text = f'{users_text.capitalize()} - ' \
               f'принятно, твой позывной успешно обновлен!'

        await User.filter(telegram_id=user).update(callsign=users_text.lower())
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=point_activation_keyboard()
        )

        raise ApplicationHandlerStop(END)

    except IntegrityError:
        text = 'Ошибка, такой позывной уже занят. Попробуй еще раз.\n\n' \
               'Напоминаю, если хочешь отменить регистрацию позывного, ' \
               'напиши /cancel в чат.'
        save_data = await update.message.reply_text(text=text)

        context.user_data['callsign_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(CREATE_OR_UPDATE_CALLSIGN)

    except ValidationError:
        text = f'Не особо это на позывной похоже, если честно.\n\n' \
               f'Давай-ка, {update.message.from_user.name}, ' \
               f'все по новой. Ну или жми /cancel, чтобы отменить ' \
               f'регистрацию позывного.'

        save_data = await update.message.reply_text(text=text)

        context.user_data['callsign_message_id'] = int(save_data.message_id)

        raise ApplicationHandlerStop(CREATE_OR_UPDATE_CALLSIGN)


async def stop_callsign_handler(update: Update,
                                context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    """
    Stops adding a callsign.
    """

    try:
        text = 'Обновление позывного отменено.'

        await context.bot.edit_message_text(
            text=text,
            chat_id=update.effective_chat.id,
            message_id=context.user_data.get('callsign_message_id'),
        )

        return END

    except BadRequest:

        return END


async def team(update: Update,
               context: CallbackContext.DEFAULT_TYPE) -> \
        CHOOSING_TEAM_ACTION:
    """
    The beginning of the user's choice of the game side.
    """

    teams = await get_teams()

    try:
        await get_user_callsign(update.message.from_user.id)

        if teams:

            text = 'Выбери сторону из предложенных ниже:\n\n' \
                   'Если хочешь отменить выбор стороны, то просто ' \
                   'вбей /team или любую другую команду. Ну или напиши ' \
                   'что-нибудь в чат.'

            save_data = await update.message.reply_text(
                text=text,
                reply_markup=await teams_keyboard(False)
            )

            context.user_data['team_message_id'] = int(save_data.message_id)

            return CHOOSING_TEAM_ACTION

        else:
            no_teams = f'Нет сторон, к которым можно примкнуть.\n' \
                       f'Попроси {CREATORS_USERNAME} добавить стороны.'

            await update.message.reply_text(
                text=no_teams
            )

            return END

    except DoesNotExist:
        user_does_not_exist = 'Без понятия кто ты, пройди регистрацию, ' \
                              'введя команду /callsign'

        await update.message.reply_text(
            text=user_does_not_exist
        )

        return END


async def choose_the_team(update: Update,
                          context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    """
    Assigns the selected side to the user.
    """

    await update.callback_query.answer()

    if await get_user_callsign(update.callback_query.from_user.id) is not None:
        callback_data = re.sub(r'^TEAM_COLOR_', '', update.callback_query.data)
        callback_data = callback_data.lower()

        try:
            user_id = update.callback_query.from_user.id
            await update_players_team(
                telegram_id=int(user_id),
                team_name=str(callback_data)
            )

            await update_users_in_game(
                telegram_id=user_id,
                status=True
            )

            text = f'Выбрана сторона: {callback_data.capitalize()}'
            await update.callback_query.edit_message_text(
                text=text
            )

            return END

        except DoesNotExist:
            text = 'Что-то пошло не так. Скорее всего ты не ' \
                   'зарегистрирован(а). Можешь сделать это при ' \
                   'помощи команды /callsign'
            await update.callback_query.edit_message_text(text=text)

        return END

    else:
        text = 'Ты не зарегистрировал свой позывной в чат-боте.\n\n' \
               'Вспользуйся командой /callsign и введи свой позывной!'
        await update.callback_query.edit_message_text(text=text)

        return END


async def stop_team_handler(update: Update,
                            context: CallbackContext.DEFAULT_TYPE) -> \
        END:
    """
    Stops the side selection.
    """

    try:
        text = 'Выбор стороны прекращен. Если нужно выбрать сторону, ' \
               'повторно введи /team в чат.'
        await context.bot.edit_message_text(
            text=text,
            chat_id=update.effective_chat.id,
            message_id=context.user_data.get('team_message_id')
        )

        return END

    except BadRequest:

        return END

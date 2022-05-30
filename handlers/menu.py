import re
import string

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from tortoise.exceptions import IntegrityError, ValidationError

from settings.settings import CREATORS_ID

from database.user.models import User

CREATE_OR_UPDATE_CALLSIGN = 0

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
                   context: CallbackContext.DEFAULT_TYPE) -> int:
    user = update.message.from_user.id

    if user == int(CREATORS_ID):
        await User.get_or_create(telegram_id=user,
                                 is_member=True,
                                 is_admin=True)
    else:
        await User.get_or_create(telegram_id=user)

    await update.message.reply_text(
        'Введи свой позывной в текстовом поле и нажми отправить.\n\n'
        'Позывной должен быть уникальным, поэтому, если он уже занят, '
        'то я тебя уведмлю об этом. Так же в позывном нельзя '
        'использовать спец. символы, я их просто удалю.\n\n'
        'Для отмены регистрации позывного напиши /cancel в чат.'
    )

    return CREATE_OR_UPDATE_CALLSIGN


async def commit_callsign(update: Update,
                          context: CallbackContext.DEFAULT_TYPE) -> int:
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
            'Ошибка, такой позывной уже занят. Попробуй еще раз.\n\n'
            'Напоминаю, если хочешь отменить регистрацию позывного, '
            'напиши /cancel в чат.'
        )
    except ValidationError:
        await update.message.reply_text(
            'Не особо это на позывной похоже, если честно.\n\n'
            f'Давай-ка, {update.message.from_user.name}, '
            f'все по новой.'
        )


async def stop_calsign(update: Update,
                          context: CallbackContext.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Обновление позывного отменено.'
    )

    return END

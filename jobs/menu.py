from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from tortoise.exceptions import IntegrityError

from database.user.models import User

ENTER_CALLSIGN = 1


async def start(update: Update,
                context: CallbackContext) -> None:
    """Say 'Hello!' to user and inform about abilities of the bot"""
    user = update.message.from_user.id

    await User.get_or_create(telegram_id=user)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Тут приветственное сообщение'
    )


async def start_callsign(update: Update, _) -> int:
    user = update.message.from_user.id

    await User.get_or_create(telegram_id=user)
    await update.message.reply_text('Введи позывной')

    return ENTER_CALLSIGN


async def enter_callsign(update: Update, _) -> int:
    user = update.message.from_user.id
    text = update.message.text

    try:
        await User.filter(telegram_id=user).update(callsign=text)
        await update.message.reply_text('Ок')

        return ConversationHandler.END

    except IntegrityError:
        await update.message.reply_text('Не ок, пробуй заново')


async def cancel_callsign(update: Update, _) -> int:
    await update.message.reply_text('Отменено')

    return ConversationHandler.END

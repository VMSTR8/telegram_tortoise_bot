from typing import NoReturn

from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode


async def unrecognized_command(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> NoReturn:
    """
    Sends a message with commands available to users.
    """

    text = '<b>Для пользователей доступны следующие команды:</b>\n\n' \
           '/callsign - регистрация своего позывного в боте\n' \
           '/team - выбор игровой стороны\n' \
           '/admin - вызвать админ-меню'

    await update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML
    )

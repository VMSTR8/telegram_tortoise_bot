from telegram import Update
from telegram.ext import CallbackContext
from telegram.constants import ParseMode


async def unrecognized_command(update: Update,
                               context: CallbackContext.DEFAULT_TYPE) -> \
        None:
    text = f'<b>Для пользователей доступны следующие команды:</b>\n\n' \
           f'/callsign - регистрация своего позывного в боте\n' \
           f'/team - выбор игровой стороны'

    await update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML
    )

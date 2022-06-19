from telegram import Update
from telegram.ext import CallbackContext


async def unrecognized_command(update: Update,
                               context: CallbackContext.DEFAULT_TYPE) -> \
        None:
    user_input = update.message.text
    text = f'"{user_input}" - не распознано.'

    await update.message.reply_text(
        text=text
    )

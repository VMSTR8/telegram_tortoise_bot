from telegram import Update
from telegram.ext import CallbackContext

# TODO изменить приветственное сообщение


async def start(update: Update, context: CallbackContext) -> None:
    """Say 'Hello!' to user and inform about abilities of the bot"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Тут приветственное сообщение')

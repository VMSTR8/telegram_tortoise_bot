import logging

from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters

from jobs.start import start
from jobs.location import location

from settings.settings import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    location_handler = MessageHandler(filters.LOCATION, location)

    application.add_handler(start_handler)
    application.add_handler(location_handler)

    application.run_polling()

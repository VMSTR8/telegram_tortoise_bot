import logging

from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, filters, ConversationHandler
from tortoise import run_async

from database.init import init
from jobs.menu import ENTER_CALLSIGN, start, start_callsign, enter_callsign, cancel_callsign
# from jobs.location import location

from settings.settings import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    run_async(init())
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    reg_handler = ConversationHandler(
        entry_points=[CommandHandler('reg', start_callsign)],
        states={
            ENTER_CALLSIGN: [
                MessageHandler(filters.COMMAND, cancel_callsign),
                MessageHandler(filters.TEXT, enter_callsign)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_callsign)],
    )

    start_handler = CommandHandler('start', start)
    # location_handler = MessageHandler(filters.LOCATION, location)

    application.add_handler(start_handler)
    application.add_handler(reg_handler)
    # application.add_handler(location_handler)

    application.run_polling()

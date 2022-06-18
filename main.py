import logging

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ApplicationBuilder,
    filters,
    CallbackQueryHandler,
    ConversationHandler
)

from tortoise import run_async

from database.init import init

from handlers.menu import (
    CREATE_OR_UPDATE_CALLSIGN,
    CHOOSING_TEAM_ACTION,
    start,
    callsign,
    commit_callsign,
    stop_callsign_handler,
    team,
    choose_the_team,
    stop_team_handler
)

from handlers.admin_command import (
    ADD_TEAM,
    EDIT_TEAM,
    DELETE_TEAM,
    END,
    SELECTING_ACTION,
    ENTERING_TEAM,
    RESET_POINTS,
    STOPPING,
    admin,
    adding_team,
    end,
    commit_team,
    stop_admin_handler,
    restart_points
)

from handlers.location import point_activation

from settings.settings import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    # Init database connect
    run_async(init())

    # Create the app
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Create handlers
    start_handler = CommandHandler('start', start)

    reg_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler('callsign', callsign)],
        states={
            CREATE_OR_UPDATE_CALLSIGN: [
                MessageHandler(
                    filters.TEXT & (~ filters.COMMAND), commit_callsign
                )
            ]
        },
        fallbacks=[MessageHandler(filters.COMMAND, stop_callsign_handler)],
    )

    team_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler('team', team)],
        states={
            CHOOSING_TEAM_ACTION: [CallbackQueryHandler(
                callback=choose_the_team,
                pattern="^" + 'TEAM_COLOR_' + ".*$"),
            ],
        },
        fallbacks=[MessageHandler(filters.COMMAND, stop_team_handler)],
    )

    selection_handlers = [
        CallbackQueryHandler(
            adding_team, pattern="^" + str(ADD_TEAM) + "$"
        ),
        CallbackQueryHandler(
            adding_team, pattern="^" + str(EDIT_TEAM) + "$"
        ),  # adding_team временная
        CallbackQueryHandler(
            adding_team, pattern="^" + str(DELETE_TEAM) + "$"
        ),  # adding_team временная
        CallbackQueryHandler(
            restart_points, pattern="^" + str(RESET_POINTS) + "$"
        ),
        CallbackQueryHandler(
            end, pattern="^" + str(END) + "$"
        ),
    ]
    admin_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler('admin', admin)],
        states={
            SELECTING_ACTION: selection_handlers,
            ENTERING_TEAM: [MessageHandler(
                filters.TEXT & ~ filters.COMMAND, commit_team
            )],
            STOPPING: [CommandHandler('admin', admin)]
        },
        fallbacks=[MessageHandler(filters.COMMAND, stop_admin_handler)]
    )

    point_activation_handler = MessageHandler(
        filters.LOCATION, point_activation
    )

    application.add_handler(start_handler, 0)
    application.add_handler(point_activation_handler, 4)
    application.add_handler(reg_handler, 3)
    application.add_handler(team_handler, 2)
    application.add_handler(admin_handler, 1)

    # Run the app
    application.run_polling()

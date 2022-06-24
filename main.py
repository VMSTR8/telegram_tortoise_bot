import logging

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ApplicationBuilder,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

from tortoise import run_async

from database.init import init

from keyboards.keyboards import (
    ADD_TEAM,
    EDIT_TEAM,
    DELETE_TEAM,
    ADD_POINT,
    DELETE_POINT,
    BACK_TO_MENU,
    END,
)

from handlers.menu import (
    CREATE_OR_UPDATE_CALLSIGN,
    CHOOSING_TEAM_ACTION,
    start,
    callsign,
    commit_callsign,
    stop_callsign_handler,
    team,
    choose_the_team,
    stop_team_handler,
)

from handlers.admin_command import (
    SELECTING_ACTION,
    ENTER_TEAM,
    ENTER_EDITING_TEAM,
    ENTER_TEAM_NEW_DATA,
    ENTER_DELETING_TEAM,
    ENTER_POINT,
    ENTER_POINT_COORDINATES,
    ENTER_DELETING_POINT,
    admin,
    adding_team,
    editing_team,
    commit_editing_team,
    commit_update_team,
    commit_team,
    deleting_team,
    commit_deleting_team,
    adding_point,
    commit_point_name,
    commit_point_coordinates,
    restart_points,
    deleting_point,
    commit_deleting_point,
    stop_admin_handler,
)

from handlers.location import point_activation

from handlers.unrecognized import unrecognized_command

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
        fallbacks=[MessageHandler(
            filters.COMMAND, stop_callsign_handler
        )],
    )

    team_handler = ConversationHandler(
        entry_points=[CommandHandler('team', team)],
        states={
            CHOOSING_TEAM_ACTION: [CallbackQueryHandler(
                callback=choose_the_team,
                pattern="^" + 'TEAM_COLOR_' + ".*$"),
            ]
        },
        fallbacks=[MessageHandler(
            filters.TEXT, stop_team_handler
        )],
    )

    selection_handlers = [
        CallbackQueryHandler(
            adding_team, pattern="^" + str(ADD_TEAM) + "$"
        ),
        CallbackQueryHandler(
            editing_team, pattern="^" + str(EDIT_TEAM) + "$"
        ),
        CallbackQueryHandler(
            deleting_team, pattern="^" + str(DELETE_TEAM) + "$"
        ),
        CallbackQueryHandler(
            adding_point, pattern="^" + str(ADD_POINT) + "$"
        ),
        CallbackQueryHandler(
            deleting_point, pattern="^" + str(DELETE_POINT) + "$"
        ),
        CallbackQueryHandler(
            restart_points, pattern="^" + str(BACK_TO_MENU) + "$"
        ),
    ]
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin)],
        states={
            SELECTING_ACTION: selection_handlers,
            BACK_TO_MENU: [CallbackQueryHandler(
                callback=admin,
                pattern="^" + str(END) + "$"
            )],
            ENTER_TEAM: [MessageHandler(
                filters.TEXT & (~ filters.COMMAND), commit_team
            )],
            ENTER_EDITING_TEAM: [CallbackQueryHandler(
                callback=commit_editing_team,
                pattern="^" + 'TEAM_COLOR_' + ".*$"
            )],
            ENTER_TEAM_NEW_DATA: [MessageHandler(
                filters.TEXT & (~ filters.COMMAND), commit_update_team
            )],
            ENTER_DELETING_TEAM: [CallbackQueryHandler(
                callback=commit_deleting_team,
                pattern="^" + 'TEAM_COLOR_' + ".*$"
            )],
            ENTER_POINT: [MessageHandler(
                filters.TEXT & (~ filters.COMMAND), commit_point_name
            )],
            ENTER_POINT_COORDINATES: [MessageHandler(
                filters.LOCATION | filters.TEXT & (~ filters.COMMAND),
                commit_point_coordinates
            )],
            ENTER_DELETING_POINT: [CallbackQueryHandler(
                callback=commit_deleting_point,
                pattern="^" + 'POINT_' + ".*$"
            )],

        },
        fallbacks=[MessageHandler(
            filters.COMMAND, stop_admin_handler
        )],
    )

    point_activation_handler = MessageHandler(
        filters.LOCATION, point_activation
    )

    unrecognized_command_handler = MessageHandler(
        filters.TEXT | filters.COMMAND, unrecognized_command
    )

    application.add_handler(start_handler, 0)
    application.add_handler(unrecognized_command_handler, 5)
    application.add_handler(point_activation_handler, 4)
    application.add_handler(reg_handler, 3)
    application.add_handler(team_handler, 2)
    application.add_handler(admin_handler, 1)

    # Run the app
    application.run_polling()

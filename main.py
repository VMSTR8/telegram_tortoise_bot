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
    EDIT_POINT,
    DELETE_POINT,
    POINT_NAME,
    POINT_STATUS,
    POINT_LATITUDE,
    POINT_LONGITUDE,
    POINT_TIME,
    POINT_RADIUS,
    RESET_ALL,
    STOPPING,
    BACK,
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
    SELECTING_POINT,
    SELECTING_DATA_TO_CHANGE,
    ENTER_TEAM,
    ENTER_EDITING_TEAM,
    ENTER_TEAM_NEW_DATA,
    ENTER_DELETING_TEAM,
    ENTER_POINT,
    ENTER_POINT_COORDINATES,
    ENTER_DELETING_POINT,
    ENTER_EDITING_POINT_NAME,
    ENTER_EDITING_POINT_COORDINATE,
    ENTER_EDITING_POINT_TIME,
    ENTER_EDITING_POINT_RADIUS,
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
    editing_point,
    entering_editing_point,
    editing_point_name,
    editing_in_game_point,
    editing_point_latitude,
    editing_point_longitude,
    editing_point_time,
    editing_point_radius,
    commit_new_point_name,
    commit_new_point_coordinate,
    commit_new_point_time,
    commit_new_point_radius,
    deleting_point,
    commit_deleting_point,
    stop_admin_handler,
    stop_nested_admin_handler,
    end_editing_point,
    end_second_level_conv,
)

from handlers.location import point_activation

from handlers.unrecognized import unrecognized_command

from settings.settings import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main() -> None:
    """Start the bot."""

    # Init database connect
    run_async(init())

    # Create the app
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Create handlers
    # Пользователь ввел команду "start" и запустил бота
    start_handler = CommandHandler('start', start)

    # The user entered "callsign" and started registering in the bot
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

    # The user has entered "team" and selects a side
    team_handler = ConversationHandler(
        entry_points=[CommandHandler('team', team)],
        states={
            CHOOSING_TEAM_ACTION: [CallbackQueryHandler(
                callback=choose_the_team,
                pattern="^" + 'TEAM_COLOR_' + ".*$"),
            ]
        },
        fallbacks=[MessageHandler(
            filters.TEXT | filters.COMMAND, stop_team_handler
        )],
    )

    # The third level is ConversationHandle.
    # Here the user edits the point data.
    # Be sure to link to the second level of the conversation
    # so that you can return to the previous menu.
    point_data_handler = [
        CallbackQueryHandler(
            editing_point_name, pattern="^" + str(POINT_NAME) + "$"
        ),
        CallbackQueryHandler(
            editing_in_game_point, pattern="^" + str(POINT_STATUS) + "$"
        ),
        CallbackQueryHandler(
            editing_point_latitude, pattern="^" + str(POINT_LATITUDE) + "$"
        ),
        CallbackQueryHandler(
            editing_point_longitude, pattern="^" + str(POINT_LONGITUDE) + "$"
        ),
        CallbackQueryHandler(
            editing_point_time, pattern="^" + str(POINT_TIME) + "$"
        ),
        CallbackQueryHandler(
            editing_point_radius, pattern="^" + str(POINT_RADIUS) + "$"
        ),
    ]
    point_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(
            entering_editing_point,
            pattern="^" + 'POINT_' + ".*$"
        )
        ],
        states={
            SELECTING_DATA_TO_CHANGE: point_data_handler,
            ENTER_EDITING_POINT_NAME: [
                MessageHandler(
                    filters.TEXT & (~ filters.COMMAND),
                    commit_new_point_name
                )
            ],
            ENTER_EDITING_POINT_COORDINATE: [
                MessageHandler(
                    filters.TEXT & (~ filters.COMMAND),
                    commit_new_point_coordinate
                )
            ],
            ENTER_EDITING_POINT_TIME: [
                MessageHandler(
                    filters.TEXT & (~ filters.COMMAND),
                    commit_new_point_time
                )
            ],
            ENTER_EDITING_POINT_RADIUS: [
                MessageHandler(
                    filters.TEXT & (~ filters.COMMAND),
                    commit_new_point_radius
                )
            ],
        },
        fallbacks=[
            MessageHandler(
                filters.COMMAND, stop_nested_admin_handler
            ),
            CallbackQueryHandler(
                end_editing_point, pattern="^" + str(END) + "$"
            )
        ],
        map_to_parent={
            END: SELECTING_POINT,
            STOPPING: STOPPING
        }
    )

    # The second level is ConversationHandle.
    # The user enters the data editing mode
    # and gets the opportunity to return
    # to the first level of the dialog.
    second_level_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                editing_point,
                pattern="^" + str(EDIT_POINT) + "$"
            ),
            CallbackQueryHandler(
                editing_team, pattern="^" + str(EDIT_TEAM) + "$"
            ),
            CallbackQueryHandler(
                deleting_team, pattern="^" + str(DELETE_TEAM) + "$"
            ),
            CallbackQueryHandler(
                deleting_point, pattern="^" + str(DELETE_POINT) + "$"
            ),
        ],
        states={
            SELECTING_POINT: [point_conv],
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
            ENTER_DELETING_POINT: [CallbackQueryHandler(
                callback=commit_deleting_point,
                pattern="^" + 'POINT_' + ".*$"
            )],
        },
        fallbacks=[
            MessageHandler(
                filters.COMMAND, stop_nested_admin_handler
            ),
            CallbackQueryHandler(
                end_second_level_conv, pattern="^" + str(END) + "$"
            )
        ],
        map_to_parent={
            END: SELECTING_ACTION,
            STOPPING: END
        }
    )

    # The first level is ConversationHandle.
    # As soon as the user enters the "admin" command,
    # this menu is initiated.
    selection_handlers = [
        second_level_conv,
        CallbackQueryHandler(
            adding_team, pattern="^" + str(ADD_TEAM) + "$"
        ),
        CallbackQueryHandler(
            adding_point, pattern="^" + str(ADD_POINT) + "$"
        ),
        CallbackQueryHandler(
            restart_points, pattern="^" + str(RESET_ALL) + "$"
        ),
    ]
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin)],
        states={
            SELECTING_ACTION: selection_handlers,
            BACK: [CallbackQueryHandler(
                callback=admin,
                pattern="^" + str(END) + "$"
            )],
            ENTER_TEAM: [MessageHandler(
                filters.TEXT & (~ filters.COMMAND), commit_team
            )],
            ENTER_POINT: [MessageHandler(
                filters.TEXT & (~ filters.COMMAND), commit_point_name
            )],
            ENTER_POINT_COORDINATES: [MessageHandler(
                filters.LOCATION | filters.TEXT & (~ filters.COMMAND),
                commit_point_coordinates
            )],
        },
        fallbacks=[MessageHandler(
            filters.COMMAND, stop_admin_handler
        )],
    )

    # A handler that accepts the coordinates
    # sent by the user to the chat.
    point_activation_handler = MessageHandler(
        filters.LOCATION, point_activation
    )

    # For any text message outside the Conversation handle,
    # the bot informs the user of the available commands.
    unrecognized_command_handler = MessageHandler(
        filters.TEXT & (~ filters.COMMAND), unrecognized_command
    )

    application.add_handler(start_handler, 0)
    application.add_handler(unrecognized_command_handler, 5)
    application.add_handler(point_activation_handler, 4)
    application.add_handler(reg_handler, 3)
    application.add_handler(team_handler, 2)
    application.add_handler(admin_handler, 1)

    # Run the app
    application.run_polling()


if __name__ == '__main__':
    main()

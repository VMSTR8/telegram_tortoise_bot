from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from database.db_functions import get_teams

ADD_TEAM, EDIT_TEAM, DELETE_TEAM = map(chr, range(3))

ADD_POINT, EDIT_POINT, DELETE_POINT = map(chr, range(3, 6))

RESET_POINTS = map(chr, range(6, 7))

SHOW_ALL_USERS = map(chr, range(7, 8))


async def team_buttons():
    buttons = []
    lines = []
    teams = await get_teams()

    for team_title in teams:
        if len(lines) < 3:
            lines.append(
                InlineKeyboardButton(team_title.capitalize(),
                                     callback_data=str(
                                         f'TEAM_COLOR_{team_title.upper()}')
                                     )
            )
        else:
            buttons.append(lines)
            lines = [
                InlineKeyboardButton(team_title.capitalize(),
                                     callback_data=str(
                                         f'TEAM_COLOR_{team_title.upper()}')
                                     )
            ]
    buttons.append(lines)

    return buttons


async def admin_keyboad():
    buttons = [
        [
            InlineKeyboardButton("Add Team",
                                 callback_data=str(ADD_TEAM)),
            InlineKeyboardButton("Edit Team",
                                 callback_data=str(EDIT_TEAM)),
            InlineKeyboardButton("Del Team",
                                 callback_data=str(DELETE_TEAM))
        ],
        [
            InlineKeyboardButton("Add Point",
                                 callback_data=str(ADD_POINT)),
            InlineKeyboardButton("Edit Point",
                                 callback_data=str(EDIT_POINT)),
            InlineKeyboardButton("Del Point",
                                 callback_data=str(DELETE_POINT))
        ],
        [
            InlineKeyboardButton("Restart all points",
                                 callback_data=str(RESET_POINTS)),
        ],
        [
            InlineKeyboardButton("Show all users",
                                 callback_data=str(SHOW_ALL_USERS)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


async def query_team_keyboard(update: Update,
                              context: CallbackContext.DEFAULT_TYPE) -> \
        InlineKeyboardMarkup:
    await update.callback_query.answer()

    keyboard = InlineKeyboardMarkup(await team_buttons())

    return keyboard


async def team_keyboard() -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup(await team_buttons())

    return keyboard

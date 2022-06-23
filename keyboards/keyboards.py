from typing import List

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from telegram.ext import CallbackContext

from database.db_functions import get_teams, get_points

ADD_TEAM, EDIT_TEAM, DELETE_TEAM = map(chr, range(3))

ADD_POINT, EDIT_POINT, DELETE_POINT = map(chr, range(3, 6))

RESET_POINTS = map(chr, range(6, 7))

SHOW_ALL_USERS = map(chr, range(7, 8))

MENU = map(chr, range(8, 9))


async def generate_buttons(prefix: str,
                           massive: list) -> \
        List[List[InlineKeyboardButton]]:
    buttons = []
    lines = []

    for data in massive:
        if len(lines) < 3:
            lines.append(
                InlineKeyboardButton(data.capitalize(),
                                     callback_data=str(
                                         f'{prefix}_{data.upper()}'
                                     ))
            )
        else:
            buttons.append(lines)
            lines = [
                InlineKeyboardButton(data.capitalize(),
                                     callback_data=str(
                                         f'{prefix}_{data.upper()}'
                                     ))
            ]

    buttons.append(lines)

    return buttons


async def admin_keyboard() -> InlineKeyboardMarkup:
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
            InlineKeyboardButton("Del Point",
                                 callback_data=str(DELETE_POINT))
        ],
        [
            InlineKeyboardButton("Reset Players, Points & Timers",
                                 callback_data=str(RESET_POINTS)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


async def back_to_menu() -> InlineKeyboardMarkup:
    button = [
        [
            InlineKeyboardButton("Back to the Menu",
                                 callback_data=str(MENU))
        ]
    ]

    keyboard = InlineKeyboardMarkup(button)

    return keyboard


async def query_teams_keyboard(update: Update,
                               context: CallbackContext.DEFAULT_TYPE) -> \
        InlineKeyboardMarkup:
    await update.callback_query.answer()
    teams = await get_teams()

    keyboard = InlineKeyboardMarkup(
        await generate_buttons('TEAM_COLOR', teams)
    )

    return keyboard


async def teams_keyboard() -> InlineKeyboardMarkup:
    teams = await get_teams()

    keyboard = InlineKeyboardMarkup(
        await generate_buttons('TEAM_COLOR', teams)
    )

    return keyboard


async def point_activation_keyboard() -> ReplyKeyboardMarkup:
    button = [[KeyboardButton(text='АКТИВИРОВАТЬ ТОЧКУ',
                              request_location=True)]]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=button)

    return keyboard


async def query_points_keyboard(update: Update,
                                context: CallbackContext.DEFAULT_TYPE) -> \
        InlineKeyboardMarkup:
    await update.callback_query.answer()
    points = [point.get('point') for point in await get_points()]

    keyboard = InlineKeyboardMarkup(
        await generate_buttons('POINT', points)
    )

    return keyboard

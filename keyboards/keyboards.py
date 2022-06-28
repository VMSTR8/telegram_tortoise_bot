from typing import List

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from telegram.ext import CallbackContext, ConversationHandler

from database.db_functions import get_teams, get_points

ADD_TEAM, EDIT_TEAM, DELETE_TEAM = map(chr, range(3))

ADD_POINT, EDIT_POINT, DELETE_POINT = map(chr, range(3, 6))

(
    POINT_NAME,
    POINT_STATUS,
    POINT_LATITUDE,
    POINT_LONGITUDE,
    POINT_TIME,
    POINT_RADIUS
) = map(chr, range(6, 12))

RESET_ALL = map(chr, range(12, 13))

BACK = map(chr, range(13, 14))

STOPPING = map(chr, range(14, 15))

END = ConversationHandler.END


async def generate_buttons(prefix: str,
                           massive: list) -> \
        List[List[InlineKeyboardButton]]:
    buttons = []
    lines = []

    for data in massive:
        data.replace(' ', '_')
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
            InlineKeyboardButton("Доб. Сторону",
                                 callback_data=str(ADD_TEAM)),
            InlineKeyboardButton("Ред. Сторону",
                                 callback_data=str(EDIT_TEAM)),
            InlineKeyboardButton("Уд. Сторону",
                                 callback_data=str(DELETE_TEAM))
        ],
        [
            InlineKeyboardButton("Доб. Точку",
                                 callback_data=str(ADD_POINT)),
            InlineKeyboardButton("Ред. Точку",
                                 callback_data=str(EDIT_POINT)),
            InlineKeyboardButton("Уд. Точку",
                                 callback_data=str(DELETE_POINT))
        ],
        [
            InlineKeyboardButton("Сброс: игроки, точки и таймеры",
                                 callback_data=str(RESET_ALL)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    return keyboard


async def back() -> InlineKeyboardMarkup:
    button = [
        [
            InlineKeyboardButton("⬅️: Назад",
                                 callback_data=str(END))
        ]
    ]

    keyboard = InlineKeyboardMarkup(button)

    return keyboard


async def query_points_data_keyboard() -> InlineKeyboardMarkup:
    button = [
        [
            InlineKeyboardButton("Название",
                                 callback_data=str(POINT_NAME)),
            InlineKeyboardButton("Статус",
                                 callback_data=str(POINT_STATUS)),
        ],
        [
            InlineKeyboardButton("Широта",
                                 callback_data=str(POINT_LATITUDE)),
            InlineKeyboardButton("Долгота",
                                 callback_data=str(POINT_LONGITUDE)),
        ],
        [
            InlineKeyboardButton("Время",
                                 callback_data=str(POINT_TIME)),
            InlineKeyboardButton("Радиус",
                                 callback_data=str(POINT_RADIUS)),
        ],
        [
            InlineKeyboardButton("⬅️: Вернуться к точкам",
                                 callback_data=str(END)),
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
    button = [[KeyboardButton(text='📍: АКТИВИРОВАТЬ ТОЧКУ',
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

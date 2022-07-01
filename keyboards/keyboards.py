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


async def generate_buttons(
        prefix: str,
        massive: list,
        trigger: bool
) -> List[List[InlineKeyboardButton]]:
    """
    Generates a keyboard based on existing fields
    in the database. Every fourth button appears from a new line.

    :param prefix: String with first part of a button
    :param massive: List of data from database
    :param trigger: Boolean value: True if you
    want to add a "Back to menu" button
    :return: List of lists of InlineKeyboardButton
    """
    buttons = []
    lines = []

    for data in massive:
        data.replace(' ', '_')
        if len(lines) < 3:
            lines.append(
                InlineKeyboardButton(
                    data.capitalize(),
                    callback_data=str(
                        f'{prefix}_{data.upper()}'
                    )
                )
            )
        else:
            buttons.append(lines)
            lines = [
                InlineKeyboardButton(
                    data.capitalize(),
                    callback_data=str(
                        f'{prefix}_{data.upper()}'
                    )
                )
            ]
    back_button = [InlineKeyboardButton(
        "⬅️: Назад в меню",
        callback_data=str(END)
    )]

    buttons.append(lines)
    if trigger:
        buttons.append(back_button)

    return buttons


async def admin_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the generated keyboard for the admin menu.

    :return: Generated keyboard
    """
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
    """
    Returns the generated keyboard with back button.

    :return: Generated keyboard
    """
    button = [
        [
            InlineKeyboardButton("⬅️: Назад в меню",
                                 callback_data=str(END))
        ]
    ]

    keyboard = InlineKeyboardMarkup(button)

    return keyboard


async def query_points_data_keyboard() -> InlineKeyboardMarkup:
    """
    Generates and returns a keyboard for editing points.

    :return: Generated inline keyboard
    """
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


async def query_teams_keyboard(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    """
    Keyboard with a list of commands for inline message.
    """

    await update.callback_query.answer()
    teams = await get_teams()

    keyboard = InlineKeyboardMarkup(
        await generate_buttons('TEAM_COLOR', teams, trigger=True)
    )

    return keyboard


async def teams_keyboard(trigger: bool) -> InlineKeyboardMarkup:
    """
    Keyboard with a list of commands not for inline message.
    """

    teams = await get_teams()

    keyboard = InlineKeyboardMarkup(
        await generate_buttons('TEAM_COLOR', teams, trigger)
    )

    return keyboard


async def point_activation_keyboard() -> ReplyKeyboardMarkup:
    """
    Adds the "ACTIVATE POINT" button at the bottom of the chatbot.
    """

    button = [[KeyboardButton(text='📍: АКТИВИРОВАТЬ ТОЧКУ',
                              request_location=True)]]

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   keyboard=button)

    return keyboard


async def query_points_keyboard(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    """
    Keyboard with a list of points for inline message.
    """

    await update.callback_query.answer()
    points = [point.get('point') for point in await get_points()]

    keyboard = InlineKeyboardMarkup(
        await generate_buttons('POINT', points, trigger=True)
    )

    return keyboard

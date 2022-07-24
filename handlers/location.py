import asyncio
import threading
from asyncio import sleep
from typing import NoReturn

from telegram import Update
from telegram.error import Forbidden

from telegram.ext import (
    CallbackContext,
    ApplicationBuilder,
    ApplicationHandlerStop,
)

from geopy import distance

from tortoise.exceptions import DoesNotExist

from database.db_functions import (
    get_points,
    update_points_team_id,
    get_users_team_id,
    get_point_time,
    update_points_in_game_status,
    get_team_title_by_team_id,
    get_users,
    get_points_in_game_status,
)

from settings.settings import BOT_TOKEN


async def success_activation(
        point_id: int,
        point: str,
        team: str
) -> NoReturn:
    """
    Sends a message to all chat users about
    the successful activation of the point.

    :param point_id: ID of the point that was activated
    :param point: Name of the point that was activated
    :param team: Name of the game side,
    which took the point out of the game
    :return: None
    """
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    await update_points_in_game_status(
        point_id=point_id,
        status=False
    )

    text = f'Оповещение для всех:\n\n' \
           f'{point.upper()} была подорвана стороной {team.upper()}!'

    for user in await get_users():
        if user['in_game']:
            try:
                await app.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=text
                )
                await sleep(0.1)
            except Forbidden:
                continue


def sync_success_activation(*args) -> NoReturn:
    """
    The function runs the asynchronous
    function synchronously.
    """

    asyncio.run(success_activation(*args))


async def coordinates(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> NoReturn:
    """
    Заполнить
    """

    context.user_data['latitude'] = None
    context.user_data['longitude'] = None

    if update.edited_message:
        context.user_data[
            'latitude'
        ] = update.edited_message.location.latitude
        context.user_data[
            'longitude'
        ] = update.edited_message.location.longitude
    else:
        context.user_data[
            'latitude'
        ] = update.message.location.latitude
        context.user_data[
            'longitude'
        ] = update.message.location.longitude


async def point_activation(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> NoReturn:
    """
    When sending coordinates to the chat,
    activates the point if it hasn't yet been
    activated by a player of the same side.
    It also starts an activation timer in
    a separate thread.
    """

    try:
        message = update.message
        pushed_button = message.text

        points = await get_points()
        user_point = [
            {
                'lat': context.user_data.get('latitude'),
                'lng': context.user_data.get('longitude')
            }
        ]

        user_point_tuple = tuple(user_point[0].values())

        team_id = await get_users_team_id(message.from_user.id)
        team_name = await get_team_title_by_team_id(team_id)

        complete_status = False

        for point in points:
            point_tuple = (point['latitude'], point['longitude'])
            dis = distance.distance(point_tuple, user_point_tuple).m

            if pushed_button == '📍: АКТИВИРОВАТЬ ТОЧКУ':

                if int(dis) <= point[
                    'radius'
                ] and not await get_points_in_game_status(
                    point_id=point['id']
                ):

                    complete_status = True

                    out_of_game_text = f'Точка {point["point"].upper()} ' \
                                       f'уже подорвана и выведена из игры!'

                    await message.reply_text(
                        text=out_of_game_text
                    )

                    raise ApplicationHandlerStop

                elif int(dis) <= point[
                    'radius'
                ] and point[
                    'team_id'
                ] != team_id:

                    timer = threading.Timer(
                        interval=await get_point_time(point_id=point['id']),
                        function=sync_success_activation,
                        args=[
                            point['id'],
                            point['point'].capitalize(),
                            team_name
                        ]
                    )

                    timer.name = point['point']

                    for thread in threading.enumerate():
                        if thread.name == point['point']:
                            thread.cancel()

                    timer.start()

                    complete_status = True

                    activation_text = f"{message.from_user.name}, " \
                                      f"{point['point'].upper()} активирована!"

                    await update_points_team_id(point_id=point['id'],
                                                team_id=team_id)

                    await message.reply_text(text=activation_text)

                    raise ApplicationHandlerStop

                elif int(dis) <= point[
                    'radius'
                ] and point[
                    'team_id'
                ] == team_id:

                    complete_status = True

                    already_active_text = 'Точка уже активирована ' \
                                          'твоей игровой стороной!'

                    await message.reply_text(
                        text=already_active_text
                    )

                    raise ApplicationHandlerStop

                elif complete_status:
                    break

                else:
                    continue

            elif pushed_button == '❌: ДЕАКТИВИРОВАТЬ ТОЧКУ':

                if int(dis) <= point[
                    'radius'
                ] and not await get_points_in_game_status(
                    point_id=point['id']
                ):
                    complete_status = True

                    out_of_game_text = f'Точка {point["point"].upper()} ' \
                                       f'уже подорвана и выведена из игры!'

                    await message.reply_text(
                        text=out_of_game_text
                    )

                    raise ApplicationHandlerStop

                elif int(dis) <= point[
                    'radius'
                ] and point['team_id'] is None:

                    complete_status = True

                    already_active_text = 'Точка еще не активирована!'

                    await message.reply_text(
                        text=already_active_text
                    )

                    raise ApplicationHandlerStop

                elif int(dis) <= point[
                    'radius'
                ]:

                    for thread in threading.enumerate():
                        if thread.name == point['point']:
                            thread.cancel()

                    await update_points_team_id(
                        point_id=point['id'],
                        team_id=None
                    )

                    deactivation_text = f"{message.from_user.name}, " \
                                        f"{point['point'].upper()} " \
                                        f"деактивирована!"

                    await message.reply_text(text=deactivation_text)

                    complete_status = True

                    raise ApplicationHandlerStop

                elif complete_status:
                    break

                else:
                    continue

            elif pushed_button == 'ℹ️: СТАТУС ТОЧКИ':
                if int(dis) <= point[
                    'radius'
                ]:
                    if point['in_game']:
                        point_status = 'В игре'
                    else:
                        point_status = 'Выведена из игры'

                    if point['team_id']:
                        team = await get_team_title_by_team_id(
                            point['team_id']
                        )
                    else:
                        team = 'Точку никто не контролирует'

                    text = f'Название точки:\n' \
                           f'{point["point"].capitalize()}\n\n' \
                           f'Статус точки:\n' \
                           f'{point_status}\n\n' \
                           f'Точка захвачена стороной:\n' \
                           f'{team.capitalize()}'

                    await message.reply_text(text=text)

                    complete_status = True

                    raise ApplicationHandlerStop

                elif complete_status:
                    break

                else:
                    continue

        if complete_status is False:
            not_reached_text = 'Ни одна из точек не была достигнута!\n\n' \
                               'P.S. Не забудь проверить, включен ли режим ' \
                               'Live Location!'
            await message.reply_text(text=not_reached_text)

        raise ApplicationHandlerStop

    except DoesNotExist:
        text = 'Чтобы активировать точку, тебе нужно примкнуть ' \
               'к игровой стороне.\n\n' \
               'Для этого необходимо зарегистрироваться при ' \
               'помощи команды:\n/callsign\n\n' \
               'Затем выбрать сторону при помощи команды:\n/team'

        await update.message.reply_text(text=text)

        raise ApplicationHandlerStop

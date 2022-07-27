import asyncio
import threading
from datetime import datetime, timedelta
from asyncio import sleep
from typing import NoReturn, List

from telegram import Update, Message
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
    update_points_data,
    get_users_team_id,
    get_point_time,
    update_points_in_game_status,
    get_team_title_by_team_id,
    get_users,
    get_points_in_game_status,
    get_user_id,
    get_user_callsign,
    get_point_expire,
)

from settings.settings import BOT_TOKEN


async def success_activation(
        point_id: int,
        point: str,
        team: str,
        callsign: str
) -> NoReturn:
    """
    Sends a message to all chat users about
    the successful activation of the point.

    :param point_id: ID of the point that was activated
    :param point: Name of the point that was activated
    :param team: Name of the game side,
    which took the point out of the game
    :param callsign: Accepts the user's callsign
    :return: None
    """
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    await update_points_in_game_status(
        point_id=point_id,
        status=False
    )

    text = f'Оповещение для всех:\n\n' \
           f'{point.upper()} была подорвана стороной {team.upper()} ' \
           f'игроком {callsign.capitalize()}!'

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
    Tracks the transmission of coordinates
    by the user and writes them to a variable.
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


async def pushed_activate_button(
        points: List[dict],
        user_point_tuple: tuple,
        message: Message
) -> NoReturn:
    """
    Activates the point where the user is located.

    :param points: List[dict] of all points in
    database.
    :param user_point_tuple: A tuple with
    coordinates sent by the user via the bot.
    :param message: An object representing a message.
    :return: None
    """
    team_id = await get_users_team_id(message.from_user.id)
    team_name = await get_team_title_by_team_id(team_id)
    user = await get_user_callsign(message.from_user.id)

    complete_status = False

    for point in points:
        point_tuple = (point['latitude'], point['longitude'])
        dis = distance.distance(point_tuple, user_point_tuple).m

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

            interval = await get_point_time(point_id=point['id'])

            timer = threading.Timer(
                interval=interval,
                function=sync_success_activation,
                args=[
                    point['id'],
                    point['point'].capitalize(),
                    team_name,
                    user
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

            await update_points_data(
                point_id=point['id'],
                team_id=team_id,
                user_id=await get_user_id(message.from_user.id),
                expire=datetime.now() + timedelta(seconds=interval)
            )

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

    if complete_status is False:
        not_reached_text = 'Ни одна из точек не была достигнута!\n\n' \
                           'P.S. Не забудь проверить, включен ли режим ' \
                           'Live Location!'
        await message.reply_text(text=not_reached_text)

    raise ApplicationHandlerStop


async def pushed_deactivate_button(
        points: List[dict],
        user_point_tuple: tuple,
        message: Message
) -> NoReturn:
    """
    Deactivates the already activated point
    where the user is located.

    :param points: List[dict] of all points in
    database.
    :param user_point_tuple: A tuple with
    coordinates sent by the user via the bot.
    :param message: An object representing a message.
    :return: None
    """

    complete_status = False

    for point in points:
        point_tuple = (point['latitude'], point['longitude'])
        dis = distance.distance(point_tuple, user_point_tuple).m

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

            await update_points_data(
                point_id=point['id'],
                team_id=None,
                user_id=None,
                expire=None
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

    if complete_status is False:
        not_reached_text = 'Ни одна из точек не была достигнута!\n\n' \
                           'P.S. Не забудь проверить, включен ли режим ' \
                           'Live Location!'
        await message.reply_text(text=not_reached_text)

    raise ApplicationHandlerStop


async def pushed_point_status_button(
        points: List[dict],
        user_point_tuple: tuple,
        message: Message
) -> NoReturn:
    """
    Shows the status of the point where
    the user is located.

    :param points: List[dict] of all points in
    database.
    :param user_point_tuple: A tuple with
    coordinates sent by the user via the bot.
    :param message: An object representing a message.
    :return: None
    """

    complete_status = False

    for point in points:
        point_tuple = (point['latitude'], point['longitude'])
        dis = distance.distance(point_tuple, user_point_tuple).m

        if int(dis) <= point[
            'radius'
        ]:
            in_game = {
                True: 'В игре',
                False: 'Выведена из игры'
            }

            team_id = {
                True: await get_team_title_by_team_id(
                    point['team_id']
                ),
                False: 'Точку никто не контролирует'
            }

            timer = await get_point_expire(
                point_id=point['id']
            )
            if timer:
                timer = timer.replace(
                    tzinfo=None
                ) - datetime.now()

                if timer.days == 0:
                    timer = f'Осталось ' \
                            f'{timer.seconds // 60} ' \
                            f'минут(ы)'
                elif timer.days > 0:
                    timer = f'Осталось ' \
                            f'{timer.days} ' \
                            f'день/дня/дней'
                else:
                    timer = 'Выведена из игры'
            else:
                timer = 'Точка еще не активирована!'

            text = f'Название точки:\n' \
                   f'{point["point"].capitalize()}\n\n' \
                   f'Статус точки:\n' \
                   f'{in_game[bool(point["in_game"])]}\n\n' \
                   f'Точка захвачена стороной:\n' \
                   f'{team_id[bool(point["team_id"])].capitalize()}\n\n' \
                   f'Таймер:\n' \
                   f'{timer}'

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


async def point_activation(
        update: Update,
        context: CallbackContext.DEFAULT_TYPE
) -> NoReturn:
    """
    When the user clicks one of the buttons
    to interact with geolocation, the bot
    either activates the point, or deactivates
    the point or outputs information about
    the point to the chat.
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

        buttons = {
            '📍: АКТИВИРОВАТЬ ТОЧКУ': pushed_activate_button,
            '❌: ДЕАКТИВИРОВАТЬ ТОЧКУ': pushed_deactivate_button,
            'ℹ️: СТАТУС ТОЧКИ': pushed_point_status_button,
        }

        await buttons.get(pushed_button)(
            points,
            user_point_tuple,
            message
        )

    except DoesNotExist:
        text = 'Чтобы активировать точку, тебе нужно примкнуть ' \
               'к игровой стороне.\n\n' \
               'Для этого необходимо зарегистрироваться при ' \
               'помощи команды:\n/callsign\n\n' \
               'Затем выбрать сторону при помощи команды:\n/team'

        await update.message.reply_text(text=text)

        raise ApplicationHandlerStop

import asyncio
import threading

from telegram import Update
from telegram.ext import CallbackContext, ApplicationBuilder

from geopy import distance

from tortoise.exceptions import DoesNotExist

from database.db_functions import (
    get_points,
    update_points_team_id,
    get_users_team_id,
    get_point_time,
    update_points_in_game_status,
    get_team_title_by_team_id,
    get_users_telegram_id,
    get_points_in_game_status
)

from settings.settings import BOT_TOKEN


async def success_activation(point_id: int,
                             point: str,
                             team: str) -> \
        None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    await update_points_in_game_status(
        point_id=point_id,
        status=False
    )

    text = f'{point.upper()} была подорвана стороной {team}.'
    for user_telegram_id in await get_users_telegram_id():

        await app.bot.send_message(chat_id=user_telegram_id, text=text)


def sync_success_activation(*args):
    asyncio.run(success_activation(*args))


async def point_activation(update: Update,
                           context: CallbackContext.DEFAULT_TYPE) -> \
        None:
    try:
        message = None

        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message

        points = await get_points()
        user_point = [
            {
                'lat': message.location.latitude,
                'lng': message.location.longitude
            }
        ]
        radius = 10

        user_point_tuple = tuple(user_point[0].values())

        team_id = await get_users_team_id(message.from_user.id)
        team_name = await get_team_title_by_team_id(team_id)

        complete_status = False

        for point in points:
            point_tuple = (point['latitude'], point['longitude'])
            dis = distance.distance(point_tuple, user_point_tuple).m

            if int(dis) <= radius and \
                    not await get_points_in_game_status(point_id=point['id']):

                complete_status = True

                out_of_game_text = f'Точка {point["point"].upper()} ' \
                                   f'уже подорвана и выведена из игры.'

                await message.reply_text(
                    text=out_of_game_text
                )

            elif int(dis) <= radius and point['team_id'] != team_id:

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

            elif int(dis) <= radius and point['team_id'] == team_id:
                complete_status = True

                already_active_text = 'Точка уже активирована ' \
                                      'твоей игровой стороной!'

                await message.reply_text(
                    text=already_active_text
                )

            elif complete_status:
                break

            else:
                continue

        if complete_status is False:
            not_reached_text = 'Ни одна из точек не была достигнута!'
            await message.reply_text(text=not_reached_text)

    except DoesNotExist:
        text = 'Чтобы активировать точку, тебе нужно примкнуть ' \
               'к игровой стороне.\n\n' \
               'Для этого необходимо зарегистрироваться при ' \
               'помощи команды:\n/callsign\n\n' \
               'Затем выбрать сторону при помощи команды:\n/team'

        await update.message.reply_text(text=text)

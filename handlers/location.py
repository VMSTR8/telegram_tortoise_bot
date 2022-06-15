from telegram import Update
from telegram.ext import CallbackContext

from geopy import distance

from tortoise.exceptions import DoesNotExist

from database.db_functions import get_points, \
    update_points_team_id, get_users_team_id


async def point_activation(update: Update,
                           context: CallbackContext) -> None:
    try:
        message = None

        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message

        points = await get_points()
        user_point = [{'lat': message.location.latitude, 'lng': message.location.longitude}]
        radius = 10

        user_point_tuple = tuple(user_point[0].values())

        team_id = await get_users_team_id(message.from_user.id)

        complete_status = False

        for point in points:
            # point = {'id': 3, 'point': 'home_point', 'latitude': 55.604003, 'longitude': 37.663903, 'team_id': None}
            point_tuple = (point['latitude'], point['longitude'])
            dis = distance.distance(point_tuple, user_point_tuple).m

            if int(dis) <= radius and point['team_id'] != team_id:
                complete_status = True
                await update_points_team_id(point_id=point['id'],
                                            team_id=team_id)

                await message.reply_text(text=f"{message.from_user.name}, "
                                              f"{point['point'].capitalize()} активирована")

            elif int(dis) <= radius and point['team_id'] == team_id:
                complete_status = True
                await message.reply_text(
                    text='Точка уже активирована твоей игровой стороной'
                )

            elif complete_status:
                break

            else:
                continue

        if complete_status is False:
            await message.reply_text('Ни одна из точек не была достигнута.')

    except DoesNotExist:
        await update.message.reply_text(
            text='Чтобы активировать точку, тебе нужно примкнуть '
                 'к игровой стороне.\n\n'
                 'Для этого необходимо зарегистрироваться при помощи команды:\n/callsign\n\n'
                 'Затем выбрать сторону при помощи команды:\n/team'
        )

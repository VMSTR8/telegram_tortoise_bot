from telegram import Update
from telegram.ext import CallbackContext

from geopy import distance

from database.crud import get_activation_status, change_activation_status
from settings.settings import CENTER_POINT_LAT, CENTER_POINT_LNG


async def location(update: Update, context: CallbackContext) -> None:
    """Send to user chat information about reaching or leaving the point in area"""
    message = None

    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message

    center_point = [{'lat': float(CENTER_POINT_LAT), 'lng': float(CENTER_POINT_LNG)}]
    user_point = [{'lat': message.location.latitude, 'lng': message.location.longitude}]
    radius = 50

    center_point_tuple = tuple(center_point[0].values())
    user_point_tuple = tuple(user_point[0].values())

    dis = distance.distance(center_point_tuple, user_point_tuple).m

    point = await get_activation_status('echo')  # TODO WIP: временное решение, реализовать нормальную работу с точками

    if int(dis) <= radius and point is False:
        await message.reply_text(f'Ты на точке, {message.from_user.name}')
        await change_activation_status('echo', True)

    elif int(dis) > radius and point is True:
        await message.reply_text(f'Ты покинул(а) точку, {message.from_user.name}')
        await change_activation_status('echo', False)

from telegram import Update
from telegram.ext import CallbackContext

from geopy import distance

from settings.settings import CENTER_POINT_LAT, CENTER_POINT_LNG

# TODO flag это временный костыль для тестов, будет переделан на работу с sqlite
flag = 0


async def location(update: Update, context: CallbackContext) -> None:
    """Send to user chat information about reaching or leaving the point in area"""
    global flag
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

    if int(dis) <= radius and flag == 0:
        await message.reply_text(f'Ты на точке, {message.from_user.name}')
        flag += 1

    elif int(dis) > radius and flag > 0:
        await message.reply_text(f'Ты покинул(а) точку, {message.from_user.name}')
        flag -= 1

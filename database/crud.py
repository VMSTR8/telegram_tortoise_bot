from tortoise import Tortoise

from database.connect import connect
from database.user.models import Location, User


# CRUDs for Location table

async def get_or_create_new_point(point_name: str, latitude: float, longitude: float) -> None:
    """
    Creates new point or returns None if point already exist.

    :param point_name: Enter point name string
    :param latitude: Enter latitude float
    :param longitude: Enter longitude float
    :return: None
    """
    await connect()
    await Location.get_or_create(point_name=point_name,
                                 latitude=latitude,
                                 longitude=longitude)
    await Tortoise.close_connections()


async def get_all_points() -> list:
    """
    Returns the list of all points in table or returns None if points doesn't exist.

    :return: List of all points in table
    """
    await connect()
    points = []
    async for point in Location.all().values():
        points.append(point)
    await Tortoise.close_connections()
    return points


async def get_point_coordinates(point_name: str) -> tuple:
    """
    Returns tuple of the point coordinates or returns None if point doesn't exist.

    :param point_name: Enter point name string
    :return: Tuple of coordinates
    """
    await connect()
    point_values = await Location.get_or_none(point_name=point_name).values()
    if not point_values:
        await Tortoise.close_connections()
    else:
        await Tortoise.close_connections()
        return point_values['latitude'], point_values['longitude']


async def update_coordinates(point_name: str, latitude: float, longitude: float) -> None:
    """
    Updates coordinates of the point or returns None if point doesn't exist.

    :param point_name: Enter point name string
    :param latitude: Enter latitude float
    :param longitude: Enter longitude float
    :return: None
    """
    await connect()
    point_values = await Location.get_or_none(point_name=point_name).values()
    if not point_values:
        await Tortoise.close_connections()
    else:
        await Location.filter(point_name=point_name).update(latitude=latitude)
        await Location.filter(point_name=point_name).update(longitude=longitude)
        await Tortoise.close_connections()


async def get_activation_status(point_name: str) -> bool:
    """
    Returns boolean activation status of the poit or returns None if point doesn't exist.

    :param point_name: Enter point name string
    :return: Boolean status of the point
    """
    await connect()
    point_values = await Location.get_or_none(point_name=point_name).values()
    if not point_values:
        await Tortoise.close_connections()
    else:
        await Tortoise.close_connections()
        return point_values['point_activation_status']


async def update_activation_status(point_name: str, point_activation_status: bool) -> None:
    """
    Updates activation status or returns None if point doesn't exist.

    :param point_name: Enter point name string
    :param point_activation_status: Enter activation status boolean
    :return: None
    """
    await connect()
    point_values = await Location.get_or_none(point_name=point_name).values()
    if point_values is None:
        await Tortoise.close_connections()
    else:
        await Location.filter(point_name=point_name).update(point_activation_status=point_activation_status)
        await Tortoise.close_connections()


# CRUDs for User table

async def get_or_create_user(telegram_user_id: int) -> None:
    """
    Creates new user or returns None if user already exist.

    :param telegram_user_id: Enter telegram ID user integer
    :return: None
    """
    await connect()
    await User.get_or_create(telegram_user_id=telegram_user_id)
    await Tortoise.close_connections()

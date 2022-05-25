from tortoise import Tortoise
from tortoise.exceptions import IntegrityError

from database.connect import connect
from database.user.models import Location, User


# CRUDs for Location table

async def get_or_create_new_point(point_name: str,
                                  latitude: float,
                                  longitude: float) -> None:
    """
    Creates a new point or returns None if the point already exists.

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
    Returns the list of dictionaries of all points in the table
    or returns an empty list if the points don't exist.

    :return: The list of dictionaries of all points in table.
    Example: [{'point_name': string}, {'point_name': string}].
    """
    await connect()
    points_values = await Location.all().values('point_name')
    await Tortoise.close_connections()
    return points_values


async def get_point_coordinates(point_name: str) -> list:
    """
    Returns the list, which contains a dictionary of the point coordinates
    or returns an empty list if the point doesn't exist.

    :param point_name: Enter point name string
    :return: The list, which contains a dictionary of the point coordinates.
    Example: [{'latitude': float, 'longitude': float}].
    """
    await connect()
    coordinate_values = await Location.filter(
        point_name=point_name).values(
        'latitude', 'longitude')
    await Tortoise.close_connections()
    return coordinate_values


async def update_coordinates(point_name: str,
                             latitude: float,
                             longitude: float) -> None:
    """
    Updates the coordinates of the point
    or returns None if the point doesn't exist.

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
        await Location.filter(
            point_name=point_name).update(latitude=latitude)
        await Location.filter(
            point_name=point_name).update(longitude=longitude)
        await Tortoise.close_connections()


async def get_activation_status(point_name: str) -> list:
    """
    Returns the list, which contains
    a dictionary activation status of the point
    or returns an empty list if the point doesn't exist.

    :param point_name: Enter point name string
    :return: The list, which contains
    a dictionary activation status of the point.
    Example: [{'point_activation_status': boolean}].
    """
    await connect()
    point_value = await Location.filter(
        point_name=point_name).values('point_activation_status')
    await Tortoise.close_connections()
    return point_value


async def update_activation_status(point_name: str,
                                   point_activation_status: bool) -> None:
    """
    Updates activation status of the point
    or returns None if the point doesn't exist.

    :param point_name: Enter point name string
    :param point_activation_status: Enter activation status boolean
    :return: None
    """
    await connect()
    await Location.filter(
        point_name=point_name).update(
        point_activation_status=point_activation_status)
    await Tortoise.close_connections()


# CRUDs for User table


async def get_or_create_user(telegram_user_id: int) -> None:
    """
    Creates a new user or returns None if the user already exists.

    :param telegram_user_id: Enter telegram id user integer
    :return: None
    """
    await connect()
    await User.get_or_create(telegram_user_id=telegram_user_id)
    await Tortoise.close_connections()


async def update_or_create_callsign(telegram_user_id: int,
                                    callsign: str) -> None:
    """
    Updates or creates user's callsign.
    If the callsign isn't unique, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param callsign: Enter callsign string
    :return: None
    """
    await connect()
    user_id = telegram_user_id
    await get_or_create_user(telegram_user_id=user_id)
    try:
        await User.filter(telegram_user_id=user_id).update(callsign=callsign)
        await Tortoise.close_connections()
    except IntegrityError:
        await Tortoise.close_connections()
        return None


async def update_is_team_member(telegram_user_id: int,
                                is_team_member: bool) -> None:
    """
    Updates user team member status.
    If the user doesn't exist, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param is_team_member: Enter team member status boolean
    :return: None
    """
    await connect()
    await User.filter(
        telegram_user_id=telegram_user_id).update(
        is_team_member=is_team_member)
    await Tortoise.close_connections()


async def update_is_admin(telegram_user_id: int, is_admin: bool) -> None:
    """
    Updates user admin status. If the user doesn't exist, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param is_admin: Enter admin status boolean
    :return: None
    """
    await connect()
    await User.filter(
        telegram_user_id=telegram_user_id).update(
        is_admin=is_admin)
    await Tortoise.close_connections()


async def get_is_team_member(telegram_user_id: int) -> list:
    """
    Returns the list, which contains a dictionary team member status of the user.
    If the user doesn't exist, returns an empty list.

    :param telegram_user_id: Enter telegram user id integer
    :return: The list, which contains
    a dictionary team member status of the user.
    Example: [{'is_team_member': boolean}].
    """
    await connect()
    user_values = await User.filter(
        telegram_user_id=telegram_user_id).values('is_team_member')
    await Tortoise.close_connections()
    return user_values


async def get_is_admin(telegram_user_id: int) -> list:
    """
    Returns the list, which contains a dictionary admin status of the user.
    If the user doesn't exist, returns empty list.

    :param telegram_user_id: Enter telegram user id integer
    :return: The list, which contains a dictionary admin status of the user.
    Example: [{'is_admin': boolean}].
    """
    await connect()
    user_values = await User.filter(
        telegram_user_id=telegram_user_id).values('is_admin')
    await Tortoise.close_connections()
    return user_values


async def get_locations_id(telegram_user_id: int) -> list:
    """
    Returns the list, which contains a dictionary location id of the user.
    If the user doesn't exist, returns empty list.

    :param telegram_user_id: Enter telegram user id integer
    :return: The list, which contains a dictionary admin status of the user.
    Example: [{'locations_id': integer}].
    """
    await connect()
    user_values = await User.filter(
        telegram_user_id=telegram_user_id).values('locations_id')
    await Tortoise.close_connections()
    return user_values


async def update_or_create_locations_id(telegram_user_id: int,
                                        locations_id: int) -> None:
    """
    Updates user location id. If the user doesn't exist, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param locations_id: Enter location id integer
    :return:
    """
    await connect()
    await User.filter(
        telegram_user_id=telegram_user_id).update(
        locations_id=locations_id)
    await Tortoise.close_connections()

from tortoise.exceptions import IntegrityError

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
    await Location.get_or_create(point_name=point_name,
                                 latitude=latitude,
                                 longitude=longitude)


async def get_all_points() -> list:
    """
    Returns the list of dictionaries of all points in the table
    or returns an empty list if the points don't exist.

    :return: The list of dictionaries of all points in table.
    Example: [{'point_name': string}, {'point_name': string}].
    """
    points_values = await Location.all().values('point_name')
    return points_values


async def get_point_coordinates(point_name: str) -> list:
    """
    Returns the list, which contains a dictionary of the point coordinates
    or returns an empty list if the point doesn't exist.

    :param point_name: Enter point name string
    :return: The list, which contains a dictionary of the point coordinates.
    Example: [{'latitude': float, 'longitude': float}].
    """
    coordinate_values = await Location.filter(
        point_name=point_name).values(
        'latitude', 'longitude')
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
    await Location.filter(point_name=point_name).update(latitude=latitude, longitude=longitude)


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
    point_value = await Location.filter(
        point_name=point_name).values('point_activation_status')
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
    await Location.filter(
        point_name=point_name).update(
        point_activation_status=point_activation_status)


# CRUDs for User table


async def get_or_create_user(telegram_user_id: int) -> None:
    """
    Creates a new user or returns None if the user already exists.

    :param telegram_user_id: Enter telegram id user integer
    :return: None
    """
    await User.get_or_create(telegram_user_id=telegram_user_id)


async def update_or_create_callsign(telegram_user_id: int,
                                    callsign: str) -> None:
    """
    Updates or creates user's callsign.
    If the callsign isn't unique, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param callsign: Enter callsign string
    :return: None
    """
    await get_or_create_user(telegram_user_id=telegram_user_id)
    try:
        await User.filter(
            telegram_user_id=telegram_user_id).update(
            callsign=callsign
        )
    except IntegrityError:
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
    await User.filter(
        telegram_user_id=telegram_user_id).update(
        is_team_member=is_team_member)


async def update_is_admin(telegram_user_id: int, is_admin: bool) -> None:
    """
    Updates user admin status. If the user doesn't exist, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param is_admin: Enter admin status boolean
    :return: None
    """
    await User.filter(
        telegram_user_id=telegram_user_id).update(
        is_admin=is_admin)


async def get_is_team_member(telegram_user_id: int) -> list:
    """
    Returns the list, which contains a dictionary team member status of the user.
    If the user doesn't exist, returns an empty list.

    :param telegram_user_id: Enter telegram user id integer
    :return: The list, which contains
    a dictionary team member status of the user.
    Example: [{'is_team_member': boolean}].
    """
    user_values = await User.filter(
        telegram_user_id=telegram_user_id).values('is_team_member')
    return user_values


async def get_is_admin(telegram_user_id: int) -> list:
    """
    Returns the list, which contains a dictionary admin status of the user.
    If the user doesn't exist, returns empty list.

    :param telegram_user_id: Enter telegram user id integer
    :return: The list, which contains a dictionary admin status of the user.
    Example: [{'is_admin': boolean}].
    """
    user_values = await User.filter(
        telegram_user_id=telegram_user_id).values('is_admin')
    return user_values


async def get_locations_id(telegram_user_id: int) -> list:
    """
    Returns the list, which contains a dictionary location id of the user.
    If the user doesn't exist, returns empty list.

    :param telegram_user_id: Enter telegram user id integer
    :return: The list, which contains a dictionary admin status of the user.
    Example: [{'locations_id': integer}].
    """
    user_values = await User.filter(
        telegram_user_id=telegram_user_id).values('locations_id')
    return user_values


async def update_or_create_locations_id(telegram_user_id: int,
                                        locations_id: int) -> None:
    """
    Updates user location id. If the user doesn't exist, returns None.

    :param telegram_user_id: Enter telegram user id integer
    :param locations_id: Enter location id integer
    :return:
    """
    await User.filter(
        telegram_user_id=telegram_user_id).update(
        locations_id=locations_id)

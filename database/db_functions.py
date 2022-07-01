from typing import List

from tortoise.exceptions import DoesNotExist

from database.user.models import Team, User, Location


async def get_user_callsign(telegram_id: int) -> str:
    """
    Returns the user's callsign. If it returns None,
    it throws an exception.

    :param telegram_id: Telegram User ID
    :return: A string with the user's callsign
    """
    callsign = await User.get(telegram_id=telegram_id).values('callsign')
    if callsign.get('callsign') is not None:
        return callsign.get('callsign')
    else:
        raise DoesNotExist


async def get_users() -> List[dict]:
    """
    Returns a list of dictionaries with user data.

    :return: List[dict] with user data.
    """
    telegram_id = await User.all().values()
    return telegram_id


async def update_users_in_game(
        telegram_id: int,
        status: bool
) -> None:
    """
    Updates the player's "in_game" status.

    :param telegram_id: Telegram User ID
    :param status: Which status should be
    passed to the player: True or False
    :return: None
    """
    await User.filter(telegram_id=telegram_id).update(in_game=status)


async def reset_all_users() -> None:
    """
    Resets the "in_game" and "team_id"
    fields to all users by assigning a null value.

    :return: None
    """
    users = await User.all().values()
    for user in users:
        await User.filter(id=user['id']).update(
            in_game=False,
            team_id=None
        )


async def get_teams() -> List[str]:
    """
    Returns a list of names of all teams.

    :return: List[str] of name od all teams.
    """
    teams = await Team.all().values('title')
    list_of_teams = [team.get('title') for team in teams]
    return list_of_teams


async def update_players_team(
        telegram_id: int,
        team_name: str
) -> None:
    """
    Assigns a command to the user. If the telegram ID
    does not exist, it throws an exception.

    :param telegram_id: Telegram User ID
    :param team_name: Name of an existing team
    :return: None
    """
    team_id = await Team.get_or_none(title=team_name).values('id')
    if await User.filter(telegram_id=telegram_id).exists():
        await User.filter(
            telegram_id=telegram_id
        ).update(team_id=team_id['id'])
    else:
        raise DoesNotExist


async def get_users_team_id(telegram_id: int) -> int:
    """
    Returns the user's team ID. If the user's
    "team_id" field is empty, it throws an exception.

    :param telegram_id: Telegram User ID
    :return: User's team ID as an integer
    """
    users_team_id = await User.get(telegram_id=telegram_id).values('team_id')
    if users_team_id.get('team_id') is not None:
        return users_team_id.get('team_id')
    else:
        raise DoesNotExist


async def get_team_title_by_team_id(team_id: int) -> str:
    """
    Returns the name of the team via the team ID request.

    :param team_id: Team ID of existing team
    :return: Team name string
    """
    team_title = await Team.get(id=team_id).values()
    return team_title['title']


async def delete_team(team_title: str) -> None:
    """
    Deletes the team from the database.

    :param team_title: Name of an existing team
    :return: None
    """
    await Team.filter(title=team_title).delete()


async def get_points() -> List[dict]:
    """
    Returns a list of dictionaries that
    contains the data of all points.

    :return: List[dict] of all points
    """
    return await Location.all().values()


async def update_points_team_id(
        point_id: int,
        team_id: int
) -> None:
    """
    Updates the Team ID for the point.

    :param point_id: ID of existing point
    :param team_id: Team ID
    :return: None
    """
    await Location.filter(
        id=point_id
    ).update(team_id=team_id)


async def get_point_time(point_id: int) -> int:
    """
    Returns the activation time of the point.

    :param point_id: ID of existing point
    :return: The activation time of a point by a float number
    """
    time = await Location.get(id=point_id).values('time')
    return time['time']


async def update_points_in_game_status(
        point_id: int,
        status: bool
) -> None:
    """
    Updates the "in_game" status for the specified point.

    :param point_id: ID of existing point.
    :param status: Which status should be
    passed to the point: True or False
    :return: None
    """
    await Location.filter(id=point_id).update(in_game=status)


async def get_points_in_game_status(point_id: int) -> bool:
    """
    Returns the "in_game" status of the point as a boolean value.

    :param point_id: ID of existing point
    :return: The boolean status of the point "in_game"
    """
    in_game = await Location.get(id=point_id).values('in_game')
    return in_game['in_game']


async def reset_all_points() -> None:
    """
    Resets the "in_game", "time", "team_id" fields
    of the Locations table, assigning a null value.

    :return: None
    """
    points = await Location.all().values()
    for point in points:
        await Location.filter(id=point['id']).update(
            in_game=True,
            time=1200.0,
            team_id=None
        )


async def delete_point(point_title: str) -> None:
    """
    Deletes the game point from the database.

    :param point_title: Name of an existing point
    :return: None
    """
    await Location.filter(point=point_title).delete()


async def get_point_info(point_title: str) -> dict:
    """
    Returns all point data in the form of a dictionary.

    :param point_title: Name of an existing point
    :return: Dictionary with point data
    """
    point = await Location.get_or_none(point=point_title).values()
    return point

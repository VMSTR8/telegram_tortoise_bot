from typing import List

from tortoise.exceptions import DoesNotExist

from database.user.models import Team, User, Location


async def get_user_callsign(telegram_id: int) -> str:
    callsign = await User.get(telegram_id=telegram_id).values('callsign')
    if callsign.get('callsign') is not None:
        return callsign.get('callsign')
    else:
        raise DoesNotExist


async def get_users() -> List[dict]:
    telegram_id = await User.all().values()
    return telegram_id


async def update_users_in_game(telegram_id: int,
                               status: bool) -> None:
    await User.filter(telegram_id=telegram_id).update(in_game=status)


async def reset_all_users() -> None:
    users = await User.all().values()
    for user in users:
        await User.filter(id=user['id']).update(
            in_game=False,
            team_id=None
        )


async def get_teams() -> List[str]:
    teams = await Team.all().values('title')
    list_of_teams = [team.get('title') for team in teams]
    return list_of_teams


async def update_players_team(telegram_id: int,
                              team: str) -> None:
    team_id = await Team.get_or_none(title=team).values('id')
    if await User.filter(telegram_id=telegram_id).exists():
        await User.filter(
            telegram_id=telegram_id
        ).update(team_id=team_id['id'])
    else:
        raise DoesNotExist


async def get_users_team_id(telegram_id: int) -> int:
    users_team_id = await User.get(telegram_id=telegram_id).values('team_id')
    if users_team_id.get('team_id') is not None:
        return users_team_id.get('team_id')
    else:
        raise DoesNotExist


async def get_team_title_by_team_id(team_id: int) -> str:
    team_title = await Team.get(id=team_id).values()
    return team_title['title']


async def delete_team(team_title: str) -> None:
    await Team.filter(title=team_title).delete()


async def get_points() -> List[dict]:
    return await Location.all().values()


async def update_points_team_id(point_id: int,
                                team_id: int) -> None:
    await Location.filter(
        id=point_id
    ).update(team_id=team_id)


async def get_point_time(point_id: int) -> int:
    time = await Location.get(id=point_id).values('time')
    return time['time']


async def update_points_in_game_status(point_id: int,
                                       status: bool) -> None:
    await Location.filter(id=point_id).update(in_game=status)


async def get_points_in_game_status(point_id: int) -> bool:
    in_game = await Location.get(id=point_id).values('in_game')
    return in_game['in_game']


async def reset_all_points() -> None:
    points = await Location.all().values()
    for point in points:
        await Location.filter(id=point['id']).update(
            in_game=True,
            time=1200.0,
            team_id=None
        )


async def delete_point(point_title: str) -> None:
    await Location.filter(point=point_title).delete()


async def get_point_info(point_title: str) -> dict:
    point = await Location.get_or_none(point=point_title).values()
    return point

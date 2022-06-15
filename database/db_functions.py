from tortoise.exceptions import DoesNotExist

from database.user.models import Team, User, Location


async def get_teams() -> list:
    teams = await Team.all().values('title')

    list_of_teams = [team.get('title') for team in teams]

    return list_of_teams


async def update_players_team(telegram_id: int,
                              team: str) -> None:
    team_id = await Team.get_or_none(title=team).values('id')
    if await User.filter(telegram_id=telegram_id).exists():
        await User.filter(telegram_id=telegram_id).update(team_id=team_id['id'])
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


async def get_points() -> list:
    return await Location.all().values()


async def update_points_team_id(point_id: int, team_id: int) -> None:
    await Location.filter(
        id=point_id
    ).update(team_id=team_id)

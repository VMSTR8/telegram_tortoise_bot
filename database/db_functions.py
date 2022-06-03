from tortoise.exceptions import DoesNotExist

from database.user.models import Team, User


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

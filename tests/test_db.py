from datetime import datetime
from typing import NoReturn

import pytest
from tortoise.contrib import test

from tortoise.exceptions import DoesNotExist

from database.db_functions import (
    User,
    Team,
    Location,
    get_user_callsign,
    get_users,
    update_users_in_game,
    reset_all_users,
    update_players_team,
    get_users_team_id,
    get_teams,
    get_team_title_by_team_id,
    delete_team,
    get_points,
    update_points_data,
    get_point_time,
    update_points_in_game_status,
    get_points_in_game_status,
    reset_all_points,
    get_point_info,
    get_user_team,
    get_user_id,
    get_point_expire,
)


@pytest.mark.usefixtures('initialize_test_db')
class TestDataBaseFunctions(test.TestCase):

    @staticmethod
    async def db_data() -> NoReturn:
        await User.bulk_create(
            [
                User(telegram_id=1,
                     callsign='player_1'),
                User(telegram_id=2,
                     callsign='player_2'),
                User(telegram_id=3),
            ]
        )

        await Team.bulk_create(
            [
                Team(title='team1'),
                Team(title='team2'),
            ]
        )

        await Location.bulk_create(
            [
                Location(point='point1',
                         latitude=0.0,
                         longitude=0.0),
                Location(point='point2',
                         latitude=-90.0,
                         longitude=90.0),
            ]
        )

    async def test_get_user_callsign(self) -> NoReturn:
        await self.db_data()

        assert await get_user_callsign(telegram_id=1) == 'player_1'
        assert await get_user_callsign(telegram_id=2) == 'player_2'

        with pytest.raises(DoesNotExist):
            await get_user_callsign(telegram_id=3)

        with pytest.raises(DoesNotExist):
            await get_user_callsign(telegram_id=999999)

    async def test_get_users(self) -> NoReturn:
        await self.db_data()
        result = await get_users()
        assert result[0]['callsign'] == 'player_1'
        assert result[1]['callsign'] == 'player_2'
        assert result[2]['callsign'] is None

    async def test_update_users_in_game(self) -> NoReturn:
        await self.db_data()

        assert await update_users_in_game(
            telegram_id=1,
            status=True
        ) is None

        assert await update_users_in_game(
            telegram_id=228,
            status=True
        ) is None

        result = await get_users()
        assert result[0]['in_game'] == 1
        assert result[1]['in_game'] == 0
        assert result[2]['in_game'] == 0

    async def test_reset_all_users(self) -> NoReturn:
        await self.db_data()

        await User.filter(id=3).update(team_id=1)

        assert await reset_all_users() is None

        result = await get_users()
        assert result[2]['team_id'] is None

    async def test_update_players_team(self) -> NoReturn:
        await self.db_data()

        assert await update_players_team(
            telegram_id=3,
            team_name='team2'
        ) is None

        with pytest.raises(DoesNotExist):
            await update_players_team(
                telegram_id=999999,
                team_name='team1'
            )

        result = await get_users()
        assert result[2]['team_id'] == 2

    async def test_get_users_team_id(self) -> NoReturn:
        await self.db_data()

        await update_players_team(telegram_id=1, team_name='team1')
        await update_players_team(telegram_id=3, team_name='team2')

        assert await get_users_team_id(telegram_id=1) == 1

        with pytest.raises(DoesNotExist):
            await get_users_team_id(telegram_id=2)

        assert await get_users_team_id(telegram_id=3) == 2

        with pytest.raises(DoesNotExist):
            await get_users_team_id(telegram_id=4)

        with pytest.raises(DoesNotExist):
            await get_users_team_id(telegram_id=999999)

    async def test_get_teams(self) -> NoReturn:
        await self.db_data()

        assert await get_teams() == ['team1', 'team2']
        await Team.get_or_create(title='team3')
        assert await get_teams() == ['team1', 'team2', 'team3']

    async def test_get_team_title_by_team_id(self) -> NoReturn:
        await self.db_data()

        assert await get_team_title_by_team_id(team_id=1) == 'team1'
        assert await get_team_title_by_team_id(team_id=2) == 'team2'

    async def test_delete_team(self) -> NoReturn:
        await self.db_data()

        assert await get_teams() == ['team1', 'team2']
        assert await delete_team('team1') is None
        assert await get_teams() == ['team2']

    async def test_get_points(self) -> NoReturn:
        await self.db_data()

        results = await get_points()
        assert results[0]['point'] == 'point1'
        assert results[1]['point'] == 'point2'

    async def test_update_points_team_id(self) -> NoReturn:
        await self.db_data()

        assert await update_points_data(
            point_id=1,
            team_id=1,
            user_id=None,
            expire=None
        ) is None

        assert await update_points_data(
            point_id=2,
            team_id=2,
            user_id=None,
            expire=None
        ) is None

        results = await get_points()
        assert results[0]['team_id'] == 1
        assert results[1]['team_id'] == 2

    async def test_get_point_time(self) -> NoReturn:
        await self.db_data()

        assert await get_point_time(point_id=1) == 1200.0
        assert await get_point_time(point_id=2) == 1200.0

    async def test_update_points_in_game_status(self) -> NoReturn:
        await self.db_data()

        assert await update_points_in_game_status(
            point_id=1,
            status=False
        ) is None

        results = await get_points()
        assert results[0]['in_game'] == 0
        assert results[1]['in_game'] == 1

    async def test_get_points_in_game_status(self) -> NoReturn:
        await self.db_data()

        assert await get_points_in_game_status(point_id=1) == 1
        assert await get_points_in_game_status(point_id=2) == 1

    async def test_reset_all_points(self) -> NoReturn:
        await self.db_data()

        await Location.filter(id=1).update(
            in_game=False,
            time=60.0,
            team_id=1
        )
        await Location.filter(id=1).update(
            in_game=False,
            team_id=2
        )

        assert await reset_all_points() is None

        results = await get_points()
        assert results[0]['in_game'] == 1
        assert results[0]['time'] == 1200.0
        assert results[0]['team_id'] is None
        assert results[1]['in_game'] == 1
        assert results[1]['team_id'] is None

    async def test_get_point_info(self) -> NoReturn:
        await self.db_data()

        results = await get_point_info('point1')
        assert results['point'] == 'point1'
        assert results['latitude'] == 0.0
        assert results['in_game'] == 1

    async def test_get_user_team(self) -> NoReturn:
        await self.db_data()

        await User.filter(telegram_id=1).update(team_id=1)

        assert await get_user_team(1) == 'team1'
        assert await get_user_team(2) is None

    async def test_get_user_id(self):
        await self.db_data()

        assert await get_user_id(telegram_id=1) == 1

        with pytest.raises(DoesNotExist):
            await get_users_team_id(telegram_id=5)

    async def test_get_point_expire(self):
        await self.db_data()

        now = datetime.now()

        await Location.filter(id=1).update(
            expire=now,
            team_id=1,
            user_id=1
        )

        result = await get_points()
        assert await get_point_expire(
            point_id=1
        ) == result[0]['expire']

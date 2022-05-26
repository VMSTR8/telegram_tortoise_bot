from tortoise.contrib import test

from database.crud import Location, User, get_or_create_new_point, \
    get_all_points, get_point_coordinates, update_coordinates, \
    get_activation_status, update_activation_status, get_or_create_user, \
    update_or_create_callsign, update_is_team_member, update_is_admin, \
    get_is_team_member, get_is_admin, get_locations_id, \
    update_or_create_locations_id


class TestCRUD(test.TestCase):

    async def test_location_crud(self):
        await Location.bulk_create([
            Location(point_name='alpha',
                     latitude=55.762166,
                     longitude=37.681155),
            Location(point_name='echo',
                     latitude=55.604003,
                     longitude=37.663903)]
        )
        await Location.filter(
            point_name='alpha').update(
            point_activation_status=True)

        assert await get_all_points() == [{'point_name': 'alpha'}, {'point_name': 'echo'}]

        assert await get_activation_status('alpha') == [{'point_activation_status': True}]

        assert await update_activation_status('center', True) is None

        assert await get_point_coordinates('echo') == [{'latitude': 55.604003, 'longitude': 37.663903}]

        assert await update_coordinates(point_name='echo', latitude=73.895963, longitude=-36.731486) is None

        assert await get_point_coordinates('echo') == [{'latitude': 73.895963, 'longitude': -36.731486}]

        assert await get_point_coordinates('charlie') == []

        assert await get_or_create_new_point('charlie', 55.641003, 37.063903) is None

        assert await get_all_points() == [{'point_name': 'alpha'}, {'point_name': 'echo'}, {'point_name': 'charlie'}]

    async def test_user_crud(self):
        await User.bulk_create([
            User(telegram_user_id=12345678),
            User(telegram_user_id=87654321),
            User(telegram_user_id=23417568),
            User(telegram_user_id=32145678)]
        )
        await Location.create(point_name='alpha', latitude=55.762166, longitude=37.681155)

        assert await get_or_create_user(87654321) is None
        assert await get_or_create_user(86753412) is None

        assert await update_or_create_callsign(87654321, 'Test_callsign') is None
        assert await update_or_create_callsign(23417568, 'Test_callsign') is None
        assert await update_or_create_callsign(22245678, 'Test_callsign_2') is None

        assert await update_is_team_member(12345678, True) is None
        assert await update_is_team_member(0o1234567, False) is None

        assert await update_is_admin(12345678, True) is None

        assert await get_is_team_member(12345678) == [{'is_team_member': True}]
        assert await get_is_team_member(0o1234567) == []

        assert await get_is_admin(12345678) == [{'is_admin': True}]
        assert await get_is_admin(87654321) == [{'is_admin': False}]

        assert await update_or_create_locations_id(12345678, 1) is None
        assert await update_or_create_locations_id(0o1234567, 1) is None

        assert await get_locations_id(12345678) == [{'locations_id': 1}]
        assert await get_locations_id(0o1234567) == []

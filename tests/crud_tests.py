from tortoise.contrib import test

from database.crud import *


class TestSomething(test.TestCase):

    async def test_get_all_points(self):
        await Location.bulk_create([Location(point_name='alpha', latitude=55.762166, longitude=37.681155),
                                   Location(point_name='echo', latitude=55.604003, longitude=37.663903)])

        assert await get_all_points() == [{'point_name': 'alpha'}, {'point_name': 'echo'}]

    async def test_get_point_coordinates(self):
        await Location.create(point_name='alpha', latitude=55.762166, longitude=37.681155)

        assert await get_point_coordinates('alpha') == [{'latitude': 55.762166, 'longitude': 37.681155}]

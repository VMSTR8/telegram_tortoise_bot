from tortoise import Tortoise

from database.connect import connect
from database.user.models import Location, User


# CRUDs for Location table

async def get_or_create_new_point(point_name: str, latitude: float, longitude: float) -> None:
    await connect()
    await Location.get_or_create(point_name=point_name,
                                 latitude=latitude,
                                 longitude=longitude)
    await Tortoise.close_connections()


async def get_all_points() -> str:
    await connect()
    async for point in Location.all().values():
        await Tortoise.close_connections()
        return point['point_name']


async def get_point_coordinates(point_name: str):
    pass


async def get_activation_status(point_name: str) -> bool:
    await connect()
    point_values = await Location.get_or_none(point_name=point_name).values()
    if not point_values:
        print('Не существует')
        await Tortoise.close_connections()
    else:
        await Tortoise.close_connections()
        return point_values['point_activation_status']


async def change_activation_status(point_name: str, point_activation_status: bool) -> None:
    await connect()
    point_values = await Location.get_or_none(point_name=point_name).values()
    if point_values is None:
        await Tortoise.close_connections()
        print('Не существует')
    else:
        await Location.filter(point_name=point_name).update(point_activation_status=point_activation_status)
        await Tortoise.close_connections()


# CRUDs for User table

async def get_or_create_user(telegram_user_id: int) -> None:
    await connect()
    await User.get_or_create(telegram_user_id=telegram_user_id)
    await Tortoise.close_connections()

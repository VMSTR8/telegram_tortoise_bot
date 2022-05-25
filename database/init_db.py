from tortoise import Tortoise, run_async

from database import config


async def init():
    await Tortoise.init(
        db_url=config.DATABASE_URL,
        modules={'models': ['database.user.models', 'aerich.models']}
    )

    await Tortoise.generate_schemas()

if __name__ == '__main__':
    run_async(init())

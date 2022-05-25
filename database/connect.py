from tortoise import Tortoise, run_async

from database import config


async def connect():
    await Tortoise.init(
        db_url=config.DATABASE_URL,
        modules={'models': ['database.user.models', 'aerich.models']}
    )

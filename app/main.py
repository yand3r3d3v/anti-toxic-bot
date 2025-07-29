import asyncio
import logging

from aiogram import Bot, Dispatcher
from core.config import config
from core.database import db
from core.toxiticy import toxic
from handlers import routers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_USERNAME = config.ADMIN_IDS


async def main():
    await db.init_tables()

    logger.info("Starting bot...")
    bot = Bot(config.TELEGRAM_BOT_TOKEN)

    dp = Dispatcher(toxic=toxic, db=db)

    # routers
    dp.include_routers(*routers)

    logger.info("Bot started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

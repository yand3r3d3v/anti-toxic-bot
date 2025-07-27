import asyncio
import logging

import aiosqlite
from aiogram import Bot, Dispatcher
from config import config
from db import Repository, SQLiteRepository
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import setup_dishka
from handlers import routers
from perspective import Perspective
from toxiticy import PerspectiveToxicity, ToxicityRepository


class ToxicityProvider(Provider):
    @provide(scope=Scope.APP)
    def get_toxiticy(self) -> ToxicityRepository:
        return PerspectiveToxicity(
            perspective=Perspective(key=config.PERSPECTIVE_API_KEY)
        )


class RepositoryProvider(Provider):
    @provide(scope=Scope.APP)
    def get_db(self) -> Repository:
        repo = SQLiteRepository(database_url=config.DATABASE_URL)
        return repo


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_USERNAME = config.ADMIN_IDS


async def init_db():
    logger.info("Initializing database...")
    async with aiosqlite.connect("mute_bot.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS mutes (
                user_id INTEGER,
                chat_id INTEGER,
                until TIMESTAMP,
                PRIMARY KEY (user_id, chat_id)
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS toxicity_scores (
                user_id INTEGER,
                chat_id INTEGER,
                score REAL,
                timestamp TIMESTAMP
            )
        """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_joins (
                user_id INTEGER,
                chat_id INTEGER,
                join_date TIMESTAMP,
                PRIMARY KEY (user_id, chat_id)
            )
        """
        )
        await db.commit()
    logger.info("Database initialized.")


async def main():
    container = make_async_container(ToxicityProvider(), RepositoryProvider())
    await init_db()

    logger.info("Starting bot...")
    bot = Bot(config.TELEGRAM_BOT_TOKEN)

    dp = Dispatcher()

    # routers
    dp.include_routers(*routers)

    logger.info("Bot started.")
    setup_dishka(router=dp, container=container, auto_inject=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

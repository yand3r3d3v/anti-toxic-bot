import asyncio
import logging

import aiosqlite
from aiogram import Bot, Dispatcher
from config import config
from handlers import routers
from perspective import Attribute, Perspective

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levellevel)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

p = Perspective(key=config.PERSPECTIVE_API_KEY)

ADMIN_USERNAME = config.ADMIN_USERNAMES


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
    await init_db()

    logger.info("Starting bot...")
    bot = Bot(config.TELEGRAM_BOT_TOKEN)

    dp = Dispatcher(bot)

    # routers
    dp.include_routers(*routers)

    logger.info("Bot started.")
    await dp.start_polling()

    # app.add_handler(CommandHandler("start", start))
    # app.add_handler(CommandHandler("muted_users", muted_users))
    # app.add_handler(
    #     CommandHandler("unmute", unmute_command, filters=filters.ChatType.GROUPS)
    # )
    # app.add_handler(CommandHandler("toxic_users", toxic_users))
    # app.add_handler(CommandHandler("mute_history", mute_history))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))


if __name__ == "__main__":
    asyncio.run(main())

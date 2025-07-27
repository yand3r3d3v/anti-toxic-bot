import logging
from dataclasses import dataclass
from typing import Iterable, Protocol

import aiosqlite

logger = logging.getLogger(__name__)


class Repository(Protocol):
    def get_toxiticy_rating(self, chat_id: int): ...
    def get_muted_users(self, chat_id: int): ...
    def delete_muted_user(self, user_id: int, chat_id: int): ...
    def get_mute_history(self, chat_id: int, page: int, items_per_page: int): ...


@dataclass
class SQLiteRepository(Repository):
    database_url: str

    async def get_toxiticy_rating(self, chat_id: int) -> Iterable[aiosqlite.Row]:
        logger.info(f"Вызван get_toxiticy_rating для {chat_id}")
        async with aiosqlite.connect(self.database_url) as db:
            async with db.execute(
                """
                SELECT user_id, AVG(score) as avg_score
                FROM toxicity_scores
                WHERE chat_id = ?
                GROUP BY user_id
                ORDER BY avg_score DESC
                LIMIT 10
                """,
                (chat_id,),
            ) as cursor:
                return await cursor.fetchall()

    async def get_muted_users(self, chat_id: int) -> Iterable[aiosqlite.Row]:
        logger.info(f"Вызван get_muted_users для {chat_id}")
        async with aiosqlite.connect(self.database_url) as db:
            async with db.execute(
                "SELECT user_id, until FROM mutes WHERE chat_id = ?", (chat_id,)
            ) as cursor:
                return await cursor.fetchall()

    async def delete_muted_user(self, user_id, chat_id: int):
        logger.info(f"Вызван delete_muted_user для {chat_id} и пользователя {user_id}")
        async with aiosqlite.connect(self.database_url) as db:
            await db.execute(
                "DELETE FROM mutes WHERE user_id = ? AND chat_id = ?",
                (user_id, chat_id),
            )
            await db.commit()

    async def get_mute_history(self, chat_id: int, page: int, items_per_page: int):
        logger.info(
            f"Вызван get_mute_history для {chat_id} страница {page}, {items_per_page}"
        )
        async with aiosqlite.connect(self.database_url) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM mutes WHERE chat_id = ?", (chat_id,)
            ) as cursor:
                total_records = (await cursor.fetchone())[0]

            async with db.execute(
                "SELECT user_id, until FROM mutes WHERE chat_id = ? ORDER BY until DESC LIMIT ? OFFSET ?",
                (chat_id, items_per_page, (page - 1) * items_per_page),
            ) as cursor:
                rows = await cursor.fetchall()

            return (total_records, rows)

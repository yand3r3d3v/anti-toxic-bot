import logging

import aiosqlite
from aiogram import Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("toxic_users"))
async def on_message(message: Message):
    logging.info("Received /toxic_users command.")
    chat_id = message.chat.id
    async with aiosqlite.connect("mute_bot.db") as db:
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
            rows = await cursor.fetchall()
            if rows:
                message_text = "😡 Антирейтинг самых токсичных пользователей:\n\n"
                for row in rows:
                    user_id, avg_score = row
                    user = (await message.bot.get_chat_member(chat_id, user_id)).user
                    message_text += f"- <a href='tg://user?id={user_id}'>{user.username or user.full_name}</a> 💩 со средним уровнем токсичности {avg_score:.2f}\n"
                message_text += "\nГоните их и порицайте! 🚫"
                await message.reply(message_text, parse_mode=ParseMode.HTML)
            else:
                await message.reply("😊 В этом чате нет токсичных пользователей.")

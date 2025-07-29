import logging

from aiogram import Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from core.database import Database

router = Router()


@router.message(Command("toxic_users"))
async def on_message(message: Message, db: Database):
    logging.info("Received /toxic_users command.")
    chat_id = message.chat.id
    rows = await db.get_toxiticy_rating(chat_id=chat_id)
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

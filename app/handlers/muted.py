import logging
from datetime import datetime

from aiogram import Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from db import Repository
from dishka import FromDishka

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("muted_users"))
async def muted_users(message: Message, repository: FromDishka[Repository]):
    logger.info("Received /muted_users command.")
    chat_id = message.chat.id
    rows = await repository.get_muted_users(chat_id=chat_id)
    if rows:
        message_text = "🚫 Временно заблокированные пользователи:\n\n"
        for row in rows:
            user_id, until = row
            until = datetime.fromisoformat(until)
            user = (await message.bot.get_chat_member(chat_id, user_id)).user
            message_text += f"- <a href='tg://user?id={user_id}'>{user.username or user.full_name}</a> до {until.strftime('%Y-%m-%d %H:%M:%S')}\n"
        await message.reply(message_text, parse_mode=ParseMode.HTML)
    else:
        await message.reply("✅ Нет временно заблокированных пользователей.")

import logging
from datetime import datetime

import aiosqlite
from aiogram import Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from telegram_bot_pagination import InlineKeyboardPaginator

router = Router()

logger = logging.getLogger(__name__)


@router.message(Command("mute_history"))
async def on_message(message: Message):
    logger.info("Received /mute_history command.")
    chat_id = message.chat_id
    user_id = message.from_user.id
    # page = int(context.args[0]) if context.args else 1
    page = 1
    items_per_page = 10

    async with aiosqlite.connect("mute_bot.db") as db:
        async with db.execute(
            "SELECT COUNT(*) FROM mutes WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            total_records = await cursor.fetchone()[0]

        async with db.execute(
            "SELECT user_id, until FROM mutes WHERE chat_id = ? ORDER BY until DESC LIMIT ? OFFSET ?",
            (chat_id, items_per_page, (page - 1) * items_per_page),
        ) as cursor:
            rows = await cursor.fetchall()

    if rows:
        message = "📜 История блокировок:\n\n"
        for row in rows:
            user_id, until = row
            until = datetime.fromisoformat(until)
            user = await message.bot.get_chat_member(chat_id, user_id).user
            message += f"- Пользователь <a href='tg://user?id={user_id}'>{user.username or user.full_name}</a> был заблокирован до {until.strftime('%Y-%м-%d %H:%М:%S')}\n"

        paginator = InlineKeyboardPaginator(
            page_count=(total_records + items_per_page - 1) // items_per_page,
            current_page=page,
            data_pattern="mute_history#{page}",
        )
        await message.reply(
            message, parse_mode=ParseMode.HTML, reply_markup=paginator.markup
        )
    else:
        await message.reply("📜 Нет записей о блокировках.")

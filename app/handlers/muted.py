from datetime import datetime

from aiogram import Router
from aiogram.types import Message

router = Router()


async def muted_users(update: Update, context: CallbackContext):
    logger.info("Received /muted_users command.")
    chat_id = update.message.chat_id
    async with aiosqlite.connect("mute_bot.db") as db:
        async with db.execute(
            "SELECT user_id, until FROM mutes WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            if rows:
                message = "🚫 Временно заблокированные пользователи:\n\n"
                for row in rows:
                    user_id, until = row
                    until = datetime.fromisoformat(until)
                    user = await context.bot.get_chat_member(chat_id, user_id).user
                    message += f"- <a href='tg://user?id={user_id}'>{user.username or user.full_name}</a> до {until.strftime('%Y-%m-%d %H:%M:%S')}\n"
                await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(
                    "✅ Нет временно заблокированных пользователей."
                )

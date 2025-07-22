from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def on_message(message: Message): ...


async def toxic_users(update: Update, context: CallbackContext):
    logger.info("Received /toxic_users command.")
    chat_id = update.message.chat_id
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
                message = "😡 Антирейтинг самых токсичных пользователей:\n\n"
                for row in rows:
                    user_id, avg_score = row
                    user = await context.bot.get_chat_member(chat_id, user_id).user
                    message += f"- {user.username or user.full_name} 💩 со средним уровнем токсичности {avg_score:.2f}\n"
                message += "\nГоните их и порицайте! 🚫"
                await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(
                    "😊 В этом чате нет токсичных пользователей."
                )

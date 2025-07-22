from aiogram import Router
from aiogram.types import Message

router = Router()


async def unmute_user(context: CallbackContext):
    job = context.job or None
    chat_id, user_id = job.data if job else context.args

    logger.info(f"Unmuting user {user_id} in chat {chat_id}.")

    async with aiosqlite.connect("mute_bot.db") as db:
        await db.execute(
            "DELETE FROM mutes WHERE user_id = ? AND chat_id = ?", (user_id, chat_id)
        )
        await db.commit()

    chat = await context.bot.get_chat(chat_id)
    user = await context.bot.get_chat_member(chat_id, user_id).user
    if chat.type == "supergroup":
        await context.bot.restrict_chat_member(
            chat_id, user_id, permissions=ChatPermissions(can_send_messages=True)
        )

    await context.bot.send_message(
        chat_id,
        text=f"✅ Пользователь <a href='tg://user?id={user_id}'>{user.username or user.full_name}</a> был разблокирован.",
        parse_mode=ParseMode.HTML,
    )


async def unmute_command(update: Update, context: CallbackContext):
    username = update.message.from_user.username
    if username not in config.ADMIN_USERNAMES:
        await update.message.reply_text(
            "⛔ У вас нет прав для использования этой команды."
        )
        return

    try:
        user_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ Пожалуйста, укажите корректный ID пользователя для разблокировки."
        )
        return

    chat_id = update.message.chat_id
    await unmute_user(
        context=CallbackContext.from_update(update, context.application),
        chat_id=chat_id,
        user_id=user_id,
    )

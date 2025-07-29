import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.chat_permissions import ChatPermissions
from core.config import config
from core.database import Database

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("unmute"))
async def unmute_command(message: Message, db: Database):
    logger.info(f"Received /unmute command from {message.from_user.id}.")
    user_id = message.from_user.id
    if user_id not in config.ADMIN_IDS:
        await message.reply("У вас нет прав для использования этой команды.")
        return
    args = message.text.split()

    if len(args) < 2:
        await message.reply("Правильное использованием команды /unmute (USER_ID)")
        return

    try:
        int(args[1])
    except (IndexError, ValueError):
        await message.reply(
            "❌ Пожалуйста, укажите корректный ID пользователя для разблокировки."
        )
        return

    await unmute_user(message=message, db=db)


async def unmute_user(message: Message, db: Database, **kwargs):
    if not (chat_id := kwargs.get("chat_id", None)):
        chat_id = message.chat.id
    if not (user_id := kwargs.get("user_id", None)):
        user_id = message.text.split(" ")[1]

    logger.info(f"Unmuting user {user_id} in chat {chat_id}.")

    await db.delete_muted_user(user_id=user_id, chat_id=chat_id)

    chat = await message.bot.get_chat(chat_id)
    user = (await message.bot.get_chat_member(chat_id, user_id)).user
    if chat.type == "supergroup":
        await message.bot.restrict_chat_member(
            chat_id, user_id, permissions=ChatPermissions(can_send_messages=True)
        )

    await message.bot.send_message(
        chat_id,
        text=f"✅ Пользователь <a href='tg://user?id={user_id}'>{user.username or user.full_name}</a> был разблокирован.",
        parse_mode=ParseMode.HTML,
    )

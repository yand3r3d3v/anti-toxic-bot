import logging

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.chat_permissions import ChatPermissions
from config import config
from db import Repository
from dishka import FromDishka

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("unmute"))
async def unmute_command(message: Message, repository: FromDishka[Repository]):
    logger.info("Received /unmute command.")
    username = message.from_user.username
    if username not in config.ADMIN_USERNAMES:
        await message.reply("У вас нет прав для использования этой команды.")
        return
    args = message.split()

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

    await unmute_user(message=message, repository=repository)


async def unmute_user(message: Message, repository: Repository, **kwargs):
    if not (chat_id := kwargs.get("chat_id", None)):
        chat_id = message.chat.id
    if not (user_id := kwargs.get("user_id", None)):
        user_id = message.text.split(" ")[1]

    logger.info(f"Unmuting user {user_id} in chat {chat_id}.")

    await repository.delete_muted_user(user_id=user_id, chat_id=chat_id)

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

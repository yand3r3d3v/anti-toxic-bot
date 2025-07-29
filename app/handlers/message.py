import logging

from aiogram import F, Router
from aiogram.types import Message
from aiogram.types.chat_permissions import ChatPermissions
from core.database import Database
from core.toxiticy import ToxicityModeration
from handlers.unmute import unmute_user

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text, ~F.text.startswith("/"))
async def on_message(message: Message, toxic: ToxicityModeration, db: Database):
    user_id = message.from_user.id
    chat_id = message.chat.id
    chat_type = message.chat.type
    user = message.from_user

    result = await toxic.evulate_message(
        message=message.text, user_id=user_id, chat_id=chat_id
    )

    if result.mute:
        await unmute_user(message=message, db=db, user_id=user_id, chat_id=chat_id)

        if chat_type == "supergroup":
            await message.bot.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=result.until,
            )

            await message.reply(
                f"🚫 Пользователь @{user.username or user.full_name} был временно заблокирован на {result.duration} часов за токсичность.",
            )
        else:
            try:
                await message.delete()
                await message.reply(
                    f"🚫 Пользователь @{user.username or user.full_name} был временно заблокирован на {result.duration} часов за токсичность. Сообщения будут удаляться.",
                    quote=False,
                )
            except Exception as e:
                print(e)

import logging
from datetime import datetime, timedelta, timezone

import aiosqlite
from aiogram import F, Router
from aiogram.types import Message
from aiogram.types.chat_permissions import ChatPermissions
from dishka import FromDishka
from handlers.unmute import unmute_user
from toxiticy import ToxicityRepository

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text, ~F.text.startswith("/"))
async def on_message(
    message: Message,
    toxicticy: FromDishka[ToxicityRepository],
):
    user_id = message.from_user.id
    chat_id = message.chat.id
    chat_type = message.chat.type
    user = message.from_user

    response = await toxicticy.get_toxic_score(message=message)

    # Accumulate toxicity score
    score = max(
        response.toxicity,
        response.severe_toxicity,
        response.sexually_explicit,
        response.insult,
    )
    async with aiosqlite.connect("mute_bot.db") as db:
        await db.execute(
            "INSERT INTO toxicity_scores (user_id, chat_id, score, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, chat_id, score, datetime.now(timezone.utc)),
        )
        await db.commit()

    # Check user's join date
    async with aiosqlite.connect("mute_bot.db") as db:
        async with db.execute(
            "SELECT join_date FROM user_joins WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                join_date = datetime.fromisoformat(row[0])
                new_user = (
                    datetime.now(timezone.utc) - join_date
                ).total_seconds() < 10800  # 3 hours
            else:
                new_user = False

    # Adjust thresholds
    toxicity_threshold = 0.78
    if new_user:
        toxicity_threshold -= 0.1  # Lower threshold for new users
    if score > 0.9:
        toxicity_threshold -= 0.1  # Lower threshold for highly toxic messages

    # Check accumulated points
    accumulated_points = 0
    async with aiosqlite.connect("mute_bot.db") as db:
        async with db.execute(
            "SELECT COUNT(*) FROM toxicity_scores WHERE user_id = ? AND chat_id = ? AND score > 0.6",
            (user_id, chat_id),
        ) as cursor:
            row = await cursor.fetchone()
            accumulated_points = row[0]

    mute_duration_hours = (
        3 + (accumulated_points // 3) * 2
    )  # Increase mute duration for repeated offenders

    if (
        response.severe_toxicity > toxicity_threshold
        or response.toxicity > toxicity_threshold
        or response.sexually_explicit > toxicity_threshold
        or response.insult > toxicity_threshold
    ):
        if accumulated_points < 3:
            accumulated_points += 1
        else:
            accumulated_points = 0
            until = datetime.now(timezone.utc) + timedelta(hours=mute_duration_hours)
            async with aiosqlite.connect("mute_bot.db") as db:
                await db.execute(
                    "INSERT OR REPLACE INTO mutes (user_id, chat_id, until) VALUES (?, ?, ?)",
                    (user_id, chat_id, until),
                )
                await db.commit()

            logger.info(f"User {user_id} muted until {until}.")

            await unmute_user(message=message, user_id=user_id, chat_id=chat_id)

            if chat_type == "supergroup":
                await message.bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until,
                )

                await message.reply(
                    f"🚫 Пользователь @{user.username or user.full_name} был временно заблокирован на {mute_duration_hours} часов за токсичность.",
                )
            else:
                await message.delete()
                await message.reply(
                    f"🚫 Пользователь @{user.username or user.full_name} был временно заблокирован на {mute_duration_hours} часов за токсичность. Сообщения будут удаляться.",
                    quote=False,
                )

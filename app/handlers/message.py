from datetime import datetime, timedelta, timezone

from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def on_message(message: Message): ...


async def check_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user = update.message.from_user

    logger.info(f"Checking message from user {user_id} in chat {chat_id}.")

    response = await p.score(
        text,
        attributes=[
            Attribute.SEVERE_TOXICITY,
            Attribute.TOXICITY,
            Attribute.SEXUALLY_EXPLICIT,
            Attribute.INSULT,
        ],
    )

    logger.info(
        f"Perspective API response for user {user_id}: {[response.toxicity, response.severe_toxicity, response.sexually_explicit, response.insult]}"
    )

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

            context.job_queue.run_once(
                unmute_user,
                when=until,
                data=(chat_id, user_id),
                name=f"{chat_id}_{user_id}",
            )

            if chat_type == "supergroup":
                await context.bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=until,
                )

                await update.message.reply_text(
                    f"🚫 Пользователь @{user.username or user.full_name} был временно заблокирован на {mute_duration_hours} часов за токсичность.",
                )
            else:
                await update.message.delete()
                await update.message.reply_text(
                    f"🚫 Пользователь @{user.username or user.full_name} был временно заблокирован на {mute_duration_hours} часов за токсичность. Сообщения будут удаляться.",
                    quote=False,
                )

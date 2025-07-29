import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from aiosqlite import Connection
from perspective import Attribute, Perspective, Score

from .config import config
from .database import Database, db

logger = logging.getLogger(__name__)


class Toxicity:
    def __init__(self, perspective: Perspective):
        self.perspective = perspective

    async def get_toxic_score(self, message: str) -> Score:
        logger.info(f"Checking message {message}.")
        try:
            score = await self.perspective.score(
                message,
                attributes=[
                    Attribute.SEVERE_TOXICITY,
                    Attribute.TOXICITY,
                    Attribute.SEXUALLY_EXPLICIT,
                    Attribute.INSULT,
                ],
            )
            logger.info(
                f"Perspective API response for message {message}: {[score.toxicity, score.severe_toxicity, score.sexually_explicit, score.insult]}"
            )
        except ConnectionError as e:
            logger.error(f"Произошла ошибка при попытке подключения к API: {str(e)}")
        except ValueError as e:
            logger.error(
                f"Произошла ошибка при попытки получить данные о сообщении: {str(e)}"
            )
        return score


@dataclass
class Result:
    mute: bool
    duration: int
    until: int


@dataclass
class ToxicityModeration:
    db: Database
    toxic: Toxicity

    async def evulate_message(self, message: str, user_id: int, chat_id: int) -> Result:
        response = await self.toxic.get_toxic_score(message=message)
        async with self.db.get_session() as session:
            new_user = await self._users_join(
                session=session, user_id=user_id, chat_id=chat_id
            )
            score = await self._accumulated_score(
                session=session, response=response, user_id=user_id, chat_id=chat_id
            )
            mute_duration, until = await self._get_mute_duration(
                session=session,
                response=response,
                new_user=new_user,
                score=score,
                user_id=user_id,
                chat_id=chat_id,
            )

            if mute_duration:
                return Result(mute=True, duration=mute_duration, until=until)
            return Result(mute=False, duration=0, until=0)

    async def _users_join(
        self, session: Connection, user_id: int, chat_id: int
    ) -> bool:
        async with session.execute(
            "SELECT join_date FROM user_joins WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                join_date = datetime.fromisoformat(row[0])
                new_user = (
                    datetime.now(datetime.timezone.utc) - join_date
                ).total_seconds() < 10800  # 3 hours
            else:
                new_user = False

        return new_user

    async def _accumulated_score(
        self, session: Connection, response: Score, user_id: int, chat_id: int
    ):
        # Accumulate toxicity score
        score = max(
            response.toxicity,
            response.severe_toxicity,
            response.sexually_explicit,
            response.insult,
        )
        await session.execute(
            "INSERT INTO toxicity_scores (user_id, chat_id, score, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, chat_id, score, datetime.now(timezone.utc)),
        )
        await session.commit()

        return score

    async def _get_mute_duration(
        self,
        session: Connection,
        response: Score,
        new_user: bool,
        score: int,
        user_id: int,
        chat_id: int,
    ) -> int | None:
        # Adjust thresholds
        toxicity_threshold = 0.78
        if new_user:
            toxicity_threshold -= 0.1  # Lower threshold for new users
        if score > 0.9:
            toxicity_threshold -= 0.1  # Lower threshold for highly toxic messages

        # Check accumulated points
        accumulated_points = 0
        async with session.execute(
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
                until = datetime.now(timezone.utc) + timedelta(
                    hours=mute_duration_hours
                )
                await session.execute(
                    "INSERT OR REPLACE INTO mutes (user_id, chat_id, until) VALUES (?, ?, ?)",
                    (user_id, chat_id, until),
                )
                await session.commit()

                logger.info(f"User {user_id} muted until {until}.")
                return mute_duration_hours, until
        return None, None


toxic = ToxicityModeration(
    db=db, toxic=Toxicity(Perspective(config.PERSPECTIVE_API_KEY))
)

import logging
from typing import Protocol

from aiogram.types import Message
from perspective import Attribute, Perspective, Score

logger = logging.getLogger(__name__)


class ToxicityRepository(Protocol):
    async def get_toxic_score(self, message) -> Score: ...


class PerspectiveToxicity(ToxicityRepository):
    def __init__(self, perspective: Perspective):
        self.perspective = perspective

    async def get_toxic_score(self, message: Message) -> Score:
        logger.info(
            f"Checking message from user {message.from_user.id} in chat {message.chat.id}."
        )
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
                f"Perspective API response for user {message.from_user.id}: {[score.toxicity, score.severe_toxicity, score.sexually_explicit, score.insult]}"
            )
        except ConnectionError as e:
            logger.error(f"Произошла ошибка при попытке подключения к API: {str(e)}")
        except ValueError as e:
            logger.error(
                f"Произошла ошибка при попытки получить данные о сообщении: {str(e)}"
            )
        return score

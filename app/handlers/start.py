import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def on_start(message: Message):
    logger.info("Received /start command.")
    await message.reply(
        "👋 Привет! Я AntiToxicBot, который борется с токсичностью. Пиши аккуратнее!"
    )

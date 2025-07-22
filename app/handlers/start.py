from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def on_start(message: Message): ...


async def start(update: Update, context: CallbackContext):
    logger.info("Received /start command.")
    await update.message.reply_text(
        "👋 Привет! Я AntiToxicBot, который борется с токсичностью. Пиши аккуратнее!"
    )

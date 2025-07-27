from pydantic_settings import (
    BaseSettings,
)


class Config(BaseSettings):
    PERSPECTIVE_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    ADMIN_IDS: list[int]
    DATABASE_URL: str


config = Config()

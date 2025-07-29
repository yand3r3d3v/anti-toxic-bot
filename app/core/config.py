__all__ = ("config",)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    PERSPECTIVE_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    ADMIN_IDS: list[int]
    DATABASE_URL: str


config = Config()

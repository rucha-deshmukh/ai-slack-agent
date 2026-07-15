"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    slack_bot_token: str = ""
    slack_app_token: str = ""

    anthropic_api_key: str = ""
    chat_model: str = "claude-sonnet-5"

    weather_api_url: str = "https://api.open-meteo.com/v1/forecast"
    database_path: str = "data/app.db"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()

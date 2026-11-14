from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    orbotino_env: Literal["development", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    database_url: str = "sqlite+aiosqlite:///./data/orbotino.db"
    public_base_url: AnyHttpUrl = AnyHttpUrl("http://127.0.0.1:8420")

    secret_key: SecretStr
    token_encryption_key: SecretStr

    twitch_client_id: str
    twitch_client_secret: SecretStr
    twitch_bot_id: str
    twitch_owner_id: str

    discord_token: SecretStr

    spotify_client_id: str
    spotify_client_secret: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]

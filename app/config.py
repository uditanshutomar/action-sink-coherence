"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "action-sink"
    VERSION: str = "1.0.0"
    SCHEMA_VERSION: str = "v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./action_sink.db"
    MAX_EXPLANATION_LENGTH: int = 1024
    MAX_REASON_CODES: int = 10
    MAX_REASON_CODE_LENGTH: int = 64


settings = Settings()

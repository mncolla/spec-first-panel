from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def as_sqlalchemy_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+psycopg://lebane:lebane@localhost:5432/lebane"
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "lebane"
    s3_secret_key: str = "lebanelebane"
    s3_bucket: str = "departments"
    s3_region: str = "us-east-1"
    s3_public_endpoint: str = "http://localhost:9000"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("database_url", mode="before")
    @classmethod
    def _psycopg_url(cls, value: object) -> object:
        if isinstance(value, str):
            return as_sqlalchemy_url(value)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

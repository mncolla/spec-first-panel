from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()

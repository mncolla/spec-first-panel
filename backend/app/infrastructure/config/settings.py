from functools import lru_cache
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Railway injects PORT at runtime; ${{MinIO.PORT}} is not shareable and stays empty.
RAILWAY_PRIVATE_S3_PORT = 8080


def normalize_s3_endpoint(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    missing_port = parsed.port is None
    if missing_port and hostname.endswith(".railway.internal"):
        return f"{parsed.scheme}://{hostname}:{RAILWAY_PRIVATE_S3_PORT}"
    return url


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
    operator_email: str = "admin@lebane.local"
    operator_password: str = "lebanelebane"
    session_secret: str = "dev-session-secret-change-me-now"

    @field_validator("database_url", mode="before")
    @classmethod
    def _psycopg_url(cls, value: object) -> object:
        if isinstance(value, str):
            return as_sqlalchemy_url(value)
        return value

    @field_validator("s3_endpoint", mode="before")
    @classmethod
    def _s3_endpoint(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_s3_endpoint(value)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

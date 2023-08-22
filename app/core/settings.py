from typing import Optional

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application derived from environment."""

    debug: bool = True
    title: str = "Kapibara Auth Service API"
    version: str = "0.0.1"
    db_uri: Optional[PostgresDsn] = None
    postgres_user: str
    postgres_password: str
    postgres_server: str
    postgres_db: str


settings = Settings()


def get_db_url() -> str:
    return str(
        PostgresDsn.build(
            scheme="postgresql",
            username=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_server,
            path=settings.postgres_db,
        )
    )

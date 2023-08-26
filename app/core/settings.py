from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application derived from environment."""

    debug: bool = True
    title: str = "Kapibara Auth Service API"
    version: str = "0.0.1-alpha"
    db_uri: PostgresDsn | None = None
    postgres_user: str
    postgres_password: str
    postgres_server: str
    postgres_db: str
    monolith_host: str
    monolith_internal_token_header: str
    monolith_internal_token: str
    jwt_rsa_private_key: str
    jwt_rsa_public_key: str
    jwt_access_token_lifetime_minutes: int = 5
    jwt_refresh_token_lifetime_days: int = 365
    jwt_issuer: str = "KapibaraAuth"
    jwt_audience: str = "KapibaraUsers"
    default_email_from: str = "no-reply@kapi.bar"
    smtp_username: str
    smtp_password: str
    smtp_host: str
    smtp_port: int


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

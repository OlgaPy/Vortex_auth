from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the application derived from environment."""

    debug: bool = True
    title: str = "Kapibara Auth Service API"
    version: str = "0.0.1-alpha"
    environment: str = "local"
    db_uri: PostgresDsn | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_server: str | None = None
    postgres_db: str | None = None
    monolith_host: str | None = None
    monolith_internal_token_header: str | None = None
    monolith_internal_token: str | None = None
    jwt_algorithm: str = "RS512"
    jwt_rsa_private_key: str | None = None
    jwt_rsa_public_key: str | None = None
    jwt_access_token_lifetime_minutes: int = 5
    jwt_refresh_token_lifetime_days: int = 365
    jwt_issuer: str = "KapibaraAuth"
    jwt_audience: str = "KapibaraUsers"
    default_email_from: str = "no-reply@kapi.bar"
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_host: str | None = None
    smtp_port: int | None = None
    redis_host: str | None = None
    redis_port: int = 6379
    redis_db: str = "1"
    confirmation_code_length: int = 32
    confirmation_code_ttl: int = 15 * 60
    sentry_dsn: str | None = None
    username_min_length: int = 4
    username_max_length: int = 15
    username_allowed_chars_pattern: str = r"^[a-zA-Z0-9.\-_]+$"
    password_min_length: int = 4
    password_max_similarity: float = 0.7


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


def get_redis_url() -> str:
    return str(
        RedisDsn.build(
            scheme="redis",
            host=settings.redis_host,
            port=settings.redis_port,
            path=settings.redis_db,
        )
    )

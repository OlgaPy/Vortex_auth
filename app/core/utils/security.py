import datetime
import logging
import secrets
import uuid
from pathlib import Path
from smtplib import SMTPException

import bcrypt
import jwt
from fastapi import Request
from jwt import DecodeError, ExpiredSignatureError
from redis.asyncio import Redis
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from app.core.email import send_email
from app.core.enums import ConfirmationCodeType
from app.core.exceptions import (
    RefreshTokenExpired,
    RefreshTokenInvalid,
    RefreshTokenNotFound,
    WrongTokenTypeException,
)
from app.core.settings import settings
from app.core.utils.email import get_email_contents
from app.crud import crud_user_session
from app.models.user import User
from app.schemas.response_schema import AccessToken, RefreshToken
from app.schemas.security_schema import ConfirmationCodeData

logger = logging.getLogger(__name__)


def generate_hashed_password(plain_password: str | bytes) -> str:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


def check_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(plain_password, hashed_password)


async def generate_jwt_access_token(user: User, jti: str = None) -> str:
    """Generate access token."""
    token = AccessToken(
        exp=datetime.datetime.now()
        + datetime.timedelta(minutes=settings.jwt_access_token_lifetime_minutes),
        iss=settings.jwt_issuer,
        aud=settings.jwt_audience,
        jti=jti or uuid.uuid4().hex,
        user_id=str(user.uuid),
        is_active=user.is_active,
    )
    return jwt.encode(
        payload=token.model_dump(),
        key=settings.jwt_rsa_private_key,
        algorithm=settings.jwt_algorithm,
    )


async def generate_jwt_refresh_token(*, user: User, jti: str = None) -> str:
    """Generate refresh token and add into database for tracking purposes."""

    jti = jti or uuid.uuid4()
    token = RefreshToken(
        exp=datetime.datetime.now()
        + datetime.timedelta(days=settings.jwt_refresh_token_lifetime_days),
        iss=settings.jwt_issuer,
        aud=settings.jwt_audience,
        jti=str(jti),
        user_id=str(user.uuid),
    )
    return jwt.encode(
        payload=token.model_dump(),
        key=settings.jwt_rsa_private_key,
        algorithm=settings.jwt_algorithm,
    )


async def decode_token(token: str) -> dict[str, str | int | bool]:
    return jwt.decode(
        jwt=token,
        key=settings.jwt_rsa_public_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )


async def refresh_access_token(  # noqa: C901
    db: Session,
    refresh_token: str,
    request: Request | None = None,
    user_agent: str | None = None,
) -> str:
    try:
        refresh_token = await decode_token(refresh_token)
    except ExpiredSignatureError:
        logger.info("We got expired token %s", refresh_token)
        raise RefreshTokenExpired()
    except DecodeError:
        logger.info("Cannot decode token %s", refresh_token)
        raise RefreshTokenInvalid()

    if (token_type := refresh_token.get("token_type")) != "refresh":
        logger.info("User used wrong token type '%s' to refresh access token", token_type)
        raise WrongTokenTypeException()

    try:
        user_session_uuid = refresh_token["jti"]
    except KeyError:
        logger.info("Can't find jti claim in refresh token %s", refresh_token)
        raise RefreshTokenInvalid()

    try:
        user_session = await crud_user_session.get_user_session_by_uuid(
            db, user_session_uuid
        )
    except DataError:
        logger.info("Not valid jti claim format in refresh token %s", refresh_token)
        raise RefreshTokenNotFound()

    if not user_session:
        logger.info("Can't find user session from refresh token %s", refresh_token)
        raise RefreshTokenNotFound()

    if request:
        user_session.ip = request.client.host
    if user_agent:
        user_session.useragent = user_agent
    user_session.last_activity = datetime.datetime.now()
    db.commit()

    return await generate_jwt_access_token(user=user_session.user, jti=user_session_uuid)


async def generate_and_email_confirmation_code(redis: Redis, user: User):
    code = await generate_confirmation_code(
        redis, user, code_type=ConfirmationCodeType.email
    )
    email_content = await get_email_contents(
        email_type="confirm_email",
        context={
            "code": code,
            "user": user,
        },
    )
    try:
        await send_email(
            sender=settings.default_email_from,
            to=user.email,
            subject=email_content.subject,
            message=email_content.message,
            html_message=email_content.html_message,
        )
    except SMTPException:
        # Ok, what we can do here. Let's not fail user registration at least.
        # This will get logged to sentry and should be alerting us, so that we can
        # help user manually activate their account.
        logger.exception("Cannot send confirmation email to a user %s", user.username)


async def generate_confirmation_code(
    redis: Redis, user: User, code_type: ConfirmationCodeType
) -> str:
    # Divide by 2, since token_hex would generate code of said length in hex numbers
    # i.e. 2fb2 - has length of 2
    code = secrets.token_hex(settings.confirmation_code_length // 2)
    logger.info(
        "Generated %s confirmation code %s for user %s",
        code_type.value,
        code,
        user.username,
    )
    await redis.set(
        code, f"{user.uuid}:{code_type.value}", ex=settings.confirmation_code_ttl
    )
    return code


async def fetch_confirmation_code_data(
    redis: Redis, code: str
) -> ConfirmationCodeData | None:
    """Read the confirmation code from Redis."""
    code_data = await redis.get(code)
    try:
        user_uuid, code_type = code_data.decode().split(":")
    except (ValueError, TypeError):
        return None
    return ConfirmationCodeData(user_uuid=user_uuid, code_type=code_type)


def is_username_allowed_to_register(username: str) -> bool:
    usernames_blacklist_file = (
        Path(__file__).resolve().parent.parent / "data" / "usernames-blacklist.txt"
    )
    with open(usernames_blacklist_file) as f:
        usernames = {x.strip() for x in f}

    return username.lower().strip() not in usernames

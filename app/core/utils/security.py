import datetime
import logging
import secrets
import uuid
from smtplib import SMTPException

import bcrypt
import jwt
from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.email import send_email
from app.core.enums import ConfirmationCodeType
from app.core.settings import settings
from app.core.utils.email import get_email_contents
from app.models.user import User, UserSession
from app.schemas.response_schema import AccessToken, RefreshToken

logger = logging.getLogger(__name__)


async def generate_hashed_password(plain_password: str | bytes) -> str:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


def check_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    if isinstance(plain_password, str):
        plain_password = plain_password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(plain_password, hashed_password)


async def generate_jwt_access_token(user: User) -> str:
    """Generate access token."""
    token = AccessToken(
        exp=datetime.datetime.now()
        + datetime.timedelta(minutes=settings.jwt_access_token_lifetime_minutes),
        iss=settings.jwt_issuer,
        aud=settings.jwt_audience,
        jti=uuid.uuid4().hex,
        user_id=str(user.uuid),
    )
    return jwt.encode(
        payload=token.model_dump(),
        key=settings.jwt_rsa_private_key,
        algorithm="RS512",
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
        algorithm="RS512",
    )


async def create_user_session(
    *, db: Session, user: User, request: Request, user_agent: str | None
) -> UserSession:
    user_session = UserSession(user=user, ip=request.client.host, useragent=user_agent)
    db.add(user_session)
    db.commit()
    return user_session


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
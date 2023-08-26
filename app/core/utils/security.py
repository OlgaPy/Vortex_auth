import datetime
import uuid

import bcrypt
import jwt
from fastapi import Request
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.user import User, UserSession
from app.schemas.response_schema import AccessToken, RefreshToken


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
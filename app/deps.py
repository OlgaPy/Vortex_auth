import redis.asyncio as redis
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import DecodeError, ExpiredSignatureError, MissingRequiredClaimError
from pydantic import ValidationError
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from app.core.enums import TokenType
from app.core.exceptions import (
    Forbidden,
    TokenExpired,
    TokenInvalid,
    UserFromTokenNotFound,
    WrongTokenType,
)
from app.core.settings import get_redis_url
from app.core.utils.security import decode_token
from app.crud import crud_user
from app.db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_redis():
    redis_client = redis.from_url(get_redis_url())
    try:
        yield redis_client
    finally:
        await redis_client.close()


async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False, description="JWT Access token")
    ),
    db: Session = Depends(get_db),
):
    if not auth:
        raise Forbidden()
    try:
        access_token = await decode_token(auth.credentials)
    except (DecodeError, ValidationError):
        raise TokenInvalid()
    except MissingRequiredClaimError as e:
        raise TokenInvalid(message=str(e))
    except ExpiredSignatureError:
        raise TokenExpired()
    if access_token.token_type != TokenType.access.value:
        raise WrongTokenType()

    try:
        user = await crud_user.get_by_uuid(db, user_uuid=access_token.user_id)
    except DataError:
        raise TokenInvalid()
    if not user:
        raise UserFromTokenNotFound()
    return user

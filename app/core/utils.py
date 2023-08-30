from datetime import datetime, timedelta
from typing import Any, Optional, Union

import bcrypt
import jwt

from app.core.settings import settings


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


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    payload = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(payload, key=settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    # try:
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return decoded_token["sub"]
    # except jwt.JWTError:
    #     return None

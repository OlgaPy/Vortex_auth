from datetime import datetime

from pydantic import BaseModel, Field


class HTTPResponse(BaseModel):
    """Basic response schema for HTTPException."""

    detail: str


class Token(BaseModel):
    """Base JWT token."""

    exp: datetime
    nbf: datetime = Field(default_factory=datetime.now)
    iat: datetime = Field(default_factory=datetime.now)
    iss: str
    aud: str
    jti: str
    token_type: str = "access"
    user_id: str


class AccessToken(Token):
    """Access token."""

    token_type: str = "access"


class RefreshToken(Token):
    """Refresh token."""

    token_type: str = "refresh"

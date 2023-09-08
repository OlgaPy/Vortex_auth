from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import TokenType


class ErrorDetail(BaseModel):
    """Individual error details."""

    msg: str
    type: str  # noqa: VNE003


class HTTPResponse(BaseModel):
    """Basic response schema for HTTPException."""

    detail: list[ErrorDetail]


class Token(BaseModel):
    """Base JWT token."""

    exp: datetime
    nbf: datetime = Field(default_factory=datetime.now)
    iat: datetime = Field(default_factory=datetime.now)
    iss: str
    aud: str
    jti: str
    token_type: TokenType = TokenType.access
    user_id: str
    is_active: bool = False


class AccessToken(Token):
    """Access token."""

    token_type: TokenType = TokenType.access


class RefreshToken(Token):
    """Refresh token."""

    token_type: TokenType = TokenType.refresh


class TokensPair(BaseModel):
    """Access / refresh tokens."""

    access_token: str
    refresh_token: str

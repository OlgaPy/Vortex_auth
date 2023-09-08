from enum import Enum


class ConfirmationCodeType(str, Enum):
    """Enum for types of confirmation codes."""

    email = "email"
    telegram = "telegram"


class TokenType(str, Enum):
    """Enum for token types."""

    access = "access"
    refresh = "refresh"

from enum import Enum


class ConfirmationCodeType(str, Enum):
    """Enum for types of confirmation codes."""

    email = "email"
    telegram = "telegram"

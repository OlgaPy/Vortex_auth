class TokenException(Exception):
    """Base exception for all token related errors."""


class WrongTokenTypeException(TokenException):
    """Exception to raise when token type is invalid for the context of operation."""


class RefreshTokenInvalid(TokenException):
    """Exception to raise when we don't have any user session associated with token."""


class RefreshTokenExpired(TokenException):
    """Exception to raise when token is expired."""

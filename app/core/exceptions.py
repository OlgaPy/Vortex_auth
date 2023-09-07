from http import HTTPStatus


class KapibaraException(Exception):
    """Base for all exceptions."""

    status_code: int
    error_type: str
    message: str

    def __init__(
        self, error_type: str = None, message: str = None, status_code: int = None
    ):
        self.error_type = error_type or self.error_type
        self.message = message or self.message
        self.status_code = status_code or self.status_code


class WrongLoginCredentials(KapibaraException):
    """Exception to raise when can't log user in with provided credentials."""

    status_code = HTTPStatus.UNAUTHORIZED
    error_type = "wrong_credentials"
    message = "Неверный логин или пароль."


class UserRegisterException(KapibaraException):
    """Base exception for user registration process."""

    status_code = HTTPStatus.BAD_REQUEST


class UserEmailExist(UserRegisterException):
    """Exception to raise when user with provided email already exists."""

    error_type = "user_email_exist"
    message = "Пользователь с таким email уже зарегистрирован."


class UserUsernameExist(UserRegisterException):
    """Exception to raise when user with provided username already exists."""

    error_type = "username_exist"
    message = "Пользователь с таким логином уже зарегистрирован."


class UserExternalCreationError(UserRegisterException):
    """Exception to raise when cannot sync user to external service."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    error_type = "cant_register_user"
    message = "Не удалось зарегистрировать пользователя."


class TokenException(KapibaraException):
    """Base exception for all token related errors."""

    status_code: int = HTTPStatus.UNAUTHORIZED


class WrongTokenTypeException(TokenException):
    """Exception to raise when token type is invalid for the context of operation."""

    status_code = HTTPStatus.BAD_REQUEST
    error_type = "wrong_token_type"
    message = "Неверный тип токена."


class RefreshTokenInvalid(TokenException):
    """Exception to raise when we don't have any user session associated with token."""

    error_type = "token_invalid"
    message = "Неверный формат токена."


class RefreshTokenNotFound(TokenException):
    """Exception to raise when session from token not found."""

    error_type = "session_from_token_not_found"
    message = "Пользовательская сессия не найдена."


class RefreshTokenExpired(TokenException):
    """Exception to raise when token is expired."""

    error_type = "token_expired"
    message = "Истек срок действия токена."

from typing import ClassVar, Mapping, Iterable, Any
from abc import ABC
from http import HTTPStatus


__all__ = ['AppException', 'UnknownError']


class AppException(Exception, ABC):
    """Базовая ошибка приложения"""

    http_code: ClassVar[int]
    err_code: ClassVar[str]
    msg: str = ""
    data: Mapping[str, Any] = {}

    def __init__(self, msg: str = "", data: Iterable | Mapping[str, Any] = None):
        self.msg = msg
        self.data = data if data is not None else {}

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        return dict(
            message=cls.msg,
            error_code=cls.err_code,
            data=cls.data
        )


class UnknownError(AppException):
    """Неизвестная ошибка"""

    http_code = HTTPStatus.INTERNAL_SERVER_ERROR
    err_code = "unknown_error"


class NotFound(AppException):
    """Сущность не найдена"""

    http_code = HTTPStatus.NOT_FOUND
    err_code = "not_found"


class UserNotFound(NotFound):
    """Сущность не найдена"""

    err_code = "user_not_found"


class Forbidden(AppException):
    """Доступ запрещен"""

    http_code = HTTPStatus.FORBIDDEN
    err_code = "forbidden"

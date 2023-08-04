from typing import ClassVar, Mapping, Iterable, Any
from abc import ABC


__all__ = ['AppException', 'UnknownError']


class AppException(Exception, ABC):
    """Базовая ошибка приложения"""

    http_code: ClassVar[int]
    err_code: ClassVar[str]

    def __init__(self, msg: str = "", data: Iterable | Mapping[str, Any] = None):
        self.msg = msg
        self.data = data if data is not None else {}

    def to_dict(self) -> dict[str, Any]:
        return dict(
            message=self.msg,
            error_code=self.err_code,
            data=self.data
        )


class UnknownError(AppException):
    """Неизвестная ошибка"""

    http_code = 500
    err_code = "unknown_error"

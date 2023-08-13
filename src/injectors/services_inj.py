"""Инъекторы сервисов"""

from services import AuthService, UserService
from config import config
from .connections import ConnectionManager


def auth_service() -> AuthService:
    return AuthService(ConnectionManager().session)


def user_service() -> UserService:
    return UserService(ConnectionManager().session)

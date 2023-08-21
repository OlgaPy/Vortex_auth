"""Инъекторы сервисов."""

# from config import config
from services import AuthService, UserService

from .connections import ConnectionManager


def auth_service() -> AuthService:
    return AuthService(ConnectionManager().session)


def user_service() -> UserService:
    return UserService(ConnectionManager().session)

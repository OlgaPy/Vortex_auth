"""Инъекторы сервисов"""

from services import AuthService, UserService
from config import config


def auth_service() -> AuthService:
    return AuthService()


def user_service() -> UserService:
    return UserService()

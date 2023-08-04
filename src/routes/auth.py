from http import HTTPStatus

from flask import Blueprint

__all__ = ['router']

router = Blueprint("auth", "auth", url_prefix="auth")


@router.post("/login")
def login():
    """Логин пользователя"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.post("/logout")
def logout():
    """Выход из системы"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.post("/refresh")
def refresh():
    """Обновление токена"""

    return "", HTTPStatus.IM_A_TEAPOT


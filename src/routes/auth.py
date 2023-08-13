from http import HTTPStatus

from flask import Blueprint, request, jsonify

from injectors.services_inj import auth_service

__all__ = ['router']

router = Blueprint("auth", "auth", url_prefix="/auth")


@router.post("/login")
def login():
    """Логин пользователя"""

    service = auth_service()
    data = request.json
    if not isinstance(data, dict):
        return "wrong data", 400

    user_login = data.get("login")
    if user_login is None:
        return "wrong data", 400

    user_password = data.get("password")
    if user_password is None:
        return "wrong data", 400

    session = service.login(user_login, user_password)

    return jsonify({
        "sid": session.sid
    })


@router.post("/logout")
def logout():
    """Выход из системы"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.post("/refresh")
def refresh():
    """Обновление токена"""

    return "", HTTPStatus.IM_A_TEAPOT


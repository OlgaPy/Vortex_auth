from http import HTTPStatus

from flask import Blueprint

__all__ = ['router']

router = Blueprint("users", "users", url_prefix="users")

"""
Example:

from flask import request, jsonify

from injectors import services_inj as inj

@router.get("/")
def get_users():
    user_service = inj.user_service()
    page = request.args.get("page", 1)
    users = user_service.get_users(page)
    return jsonify(users)
"""


@router.get("/")
def get_users():
    """Получение списка пользователей"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.post("/")
def create_user():
    """Создание пользователя"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.get("/<user_id>")
def get_user(user_id: str):
    """Получение пользователя по id"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.route("/<user_id>", methods=["PUT", "PATCH"])
def edit_user(user_id: str):
    """Редактирование пользователя по id"""

    return "", HTTPStatus.IM_A_TEAPOT


@router.delete("/<user_id>")
def delete_user(user_id: str):
    """Удаление пользователя по id"""

    return "", HTTPStatus.IM_A_TEAPOT

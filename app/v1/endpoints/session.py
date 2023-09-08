from http import HTTPStatus

from fastapi import APIRouter, Depends

from app import deps
from app.models.user import User
from app.schemas import user_schema
from app.schemas.response_schema import HTTPResponse

router = APIRouter()


@router.get(
    "/",
    response_model=list[user_schema.UserSessionOut],
    response_description="Список всех сессий пользователя",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {
            "model": HTTPResponse,
            "description": "Срок действия токена вышел, необходима повторная "
            "авторизация.",
        },
        HTTPStatus.BAD_REQUEST: {
            "model": HTTPResponse,
            "description": "Неверный тип токена, использован `refresh_token` "
            "вместо `access_token`",
        },
        HTTPStatus.FORBIDDEN: {
            "model": HTTPResponse,
            "description": "Отсутствует заголовок авторизации",
        },
    },
)
def get_all(current_user: User = Depends(deps.get_current_user)):
    """Возвращает все сессии залогиненного пользователя.

    Сессия создается когда используется `/user/login` endpoint.

    Необходима авторизация по токену, который должен быть передан в headers.

    ```
    Authorization: Bearer <access_token>
    ```
    """
    return current_user.sessions


@router.delete("/all")
def delete_all():
    ...


@router.delete("/{session_id}")
def delete_one(session_id: str):
    ...

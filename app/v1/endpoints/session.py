from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import deps
from app.crud import crud_user_session
from app.deps import get_db
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
def get_all(
    current_user_and_session_uuid: tuple[User, str] = Depends(
        deps.get_current_user_and_session_uuid
    )
):
    """Возвращает все сессии залогиненного пользователя.

    Сессия создается когда используется `/user/login` endpoint.

    Необходима авторизация по токену, который должен быть передан в headers.

    ```
    Authorization: Bearer <access_token>
    ```
    """
    current_user, _ = current_user_and_session_uuid
    return current_user.sessions


@router.delete(
    "/",
    response_description="Сессии удалены.",
    status_code=HTTPStatus.NO_CONTENT,
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
async def delete_all(
    except_current: bool = True,
    current_user_and_session_uuid: tuple[User, str] = Depends(
        deps.get_current_user_and_session_uuid
    ),
    db: Session = Depends(get_db),
):
    """Удаляет пользовательские сессии.

    По умолчанию будут удалены все сессии, кроме текущей. Если `GET` параметр
    `except_current=false`, будут удалены все сессии, включая текущую, и пользователь
    сможет пользоваться сайтом до тех пор, пока не истечет действие `access_token`.

    Необходима авторизация по токену, который должен быть передан в headers.
    ```
    Authorization: Bearer <access_token>
    ```
    """
    current_user, session_uuid = current_user_and_session_uuid
    exclude_uuids = None
    if except_current:
        exclude_uuids = [session_uuid]
    await crud_user_session.delete_user_sessions(
        db=db, user=current_user, exclude_uuids=exclude_uuids
    )


@router.delete("/{session_id}")
def delete_one(session_id: str):
    ...

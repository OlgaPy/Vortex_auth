from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import deps
from app.core.exceptions import TokenException, WrongTokenTypeException
from app.core.utils.security import refresh_access_token
from app.custom_types.request_types import RefreshToken, UserAgent
from app.schemas import response_schema

router = APIRouter()


@router.post(
    "/refresh",
    response_model=response_schema.TokensPair,
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.CREATED: {
            "model": response_schema.TokensPair,
            "description": "Пара refresh / access токенов.",
        },
        HTTPStatus.BAD_REQUEST: {
            "model": response_schema.HTTPResponse,
            "description": "Неверный тип токена, использован access вместо refresh.",
        },
        HTTPStatus.UNAUTHORIZED: {
            "model": response_schema.HTTPResponse,
            "description": "Неверный refresh токен.",
        },
    },
)
async def refresh(
    refresh_token: RefreshToken,
    request: Request,
    db: Session = Depends(deps.get_db),
    user_agent: UserAgent = None,
):
    """Принимает `refresh_token`, проверяет его на валидность и присутствие в БД.

    Если ответ пришел с HTTP Status `400` - скорее всего был использован `access` токен,
    вместо `refresh`.

    В случае, если возвращается код `401` - необходимо заново авторизовать пользователя,
    чтобы получить новые токены.
    """
    try:
        access_token = await refresh_access_token(db, refresh_token, request, user_agent)
    except WrongTokenTypeException as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    except TokenException as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=str(e))

    return response_schema.TokensPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )

import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from tenacity import RetryError

from app import deps
from app.core.utils.security import (
    generate_and_email_confirmation_code,
    generate_jwt_access_token,
    generate_jwt_refresh_token,
)
from app.crud import crud_user, crud_user_session
from app.external.exceptions import MonolithUserCreateException
from app.schemas import user_schema
from app.schemas.response_schema import HTTPResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=user_schema.UserWithJWT,
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.CREATED: {
            "model": user_schema.UserWithJWT,
            "description": "Учетная данная пользователя создана и отправлена в монолит.",
        },
        HTTPStatus.BAD_REQUEST: {
            "model": HTTPResponse,
            "description": "Пользователь с такими данными уже существует",
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            "model": HTTPResponse,
            "description": "Ошибка синхронизации пользователя с монолитом. "
            "Необходимо повторить отправку данных.",
        },
    },
)
async def register(
    user_in: user_schema.UserCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(deps.get_redis),
    user_agent: Annotated[str | None, Header()] = None,
):
    """Регистрирует пользователя в базе Auth service и отправляет его на монолит.

    - **username** - Имя пользователя, длиной 4-16 символов. Разрешены только буквы
        латинского алфавита, цифры, дефис, подчеркивание или точки. Так же нельзя
        регистрировать имена содержащие _admin_, _moderator_ и пр.
    - **email** - Пользовательский email.
    - **password** - Пароль
    """
    if await crud_user.get_by_email(db, user_in.email):
        logger.info("User with email %s already exists", user_in.email)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован.",
        )

    if await crud_user.get_by_username(db, user_in.username):
        logger.info("User with username %s already exists", user_in.username)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Пользователь с таким логином уже зарегистрирован.",
        )

    try:
        user = await crud_user.create_user_and_sync_to_monolith(db=db, user=user_in)
    except (MonolithUserCreateException, RetryError):
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="Не удалось зарегистрировать пользователя.",
        )

    await generate_and_email_confirmation_code(redis=redis, user=user)

    user_session = await crud_user_session.create_user_session(
        db=db, user=user, request=request, user_agent=user_agent
    )
    logger.info("User %s registered successfully", user_in.username)
    return user_schema.UserWithJWT(
        uuid=user.uuid,
        username=user.username,
        email=user.email,
        access_token=await generate_jwt_access_token(user),
        refresh_token=await generate_jwt_refresh_token(
            user=user, jti=user_session.uuid
        ),
    )


@router.post("/login")
def login():
    ...

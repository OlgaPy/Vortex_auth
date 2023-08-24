import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import deps
from app.core.utils import generate_jwt_access_token, generate_jwt_refresh_token
from app.crud import crud_user
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
        HTTPStatus.BAD_GATEWAY: {
            "model": HTTPResponse,
            "description": "Ошибка синхронизации пользователя с монолитом. "
            "Необходимо повторить отправку данных.",
        },
    },
)
async def register(user_in: user_schema.UserCreate, db: Session = Depends(deps.get_db)):
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
    except MonolithUserCreateException:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Не удалось зарегистрировать пользователя.",
        )
    # TODO: create confirmation code and send to email
    logger.debug("User %s registered successfully", user_in.username)
    return user_schema.UserWithJWT(
        uuid=user.uuid,
        username=user.username,
        email=user.email,
        access_token=await generate_jwt_access_token(user),
        refresh_token=await generate_jwt_refresh_token(user),
    )


@router.post("/login")
def login():
    ...

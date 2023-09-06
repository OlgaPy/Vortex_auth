import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app import deps
from app.core.utils.security import (
    fetch_confirmation_code_data,
    generate_and_email_password_reset_instruction,
    generate_jwt_access_token,
    generate_jwt_refresh_token,
)
from app.crud import crud_user, crud_user_session
from app.crud.crud_user_session import delete_user_sessions
from app.schemas import security_schema, user_schema
from app.schemas.response_schema import HTTPResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/reset",
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.CREATED: {
            "model": HTTPResponse,
            "description": "Инструкция по восстановлению пароля отправлена на email,"
            " если он был зарегистрирован на сайте.",
        },
    },
)
async def reset(
    payload=security_schema.ResetPasswordData,
    db: Session = Depends(deps.get_db),
):
    if payload.username:
        existing_user = await crud_user.get_by_username(db, username=payload.username)
    else:
        existing_user = await crud_user.get_by_email(db, email=payload.email)

    if existing_user:
        await generate_and_email_password_reset_instruction
    else:
        logger.info("The user %s was not found in the database", existing_user)


@router.post(
    "/confirm",
    response_model=user_schema.UserUpdatedWithJWT,
    status_code=HTTPStatus.CREATED,  # returns 201
    responses={
        HTTPStatus.CREATED: {
            "model": user_schema.UserUpdatedWithJWT,
            "description": "Пароль обновлен.",
        },
        HTTPStatus.BAD_REQUEST: {
            "model": HTTPResponse,
            "description": "Произошла ошибка. Token недействителен!",
        },
    },
)
async def confirm(
    payload: security_schema.RestorePasswordData,
    request: Request,
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(deps.get_redis),
    user_agent: Annotated[str | None, Header()] = None,
):
    code_data = await fetch_confirmation_code_data(redis, payload.code)
    if not code_data:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Произошла ошибка. Token недействителен!",
        )

    logger.debug(
        "User %s is found with code_type: %s", code_data.user_uuid, code_data.code_type
    )

    user = await crud_user.get_by_uuid(db, user_uuid=code_data.user_uuid)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Произошла ошибка. Такого юзера нет в системе!",
        )

    try:
        user_in_update = user_schema.UserPasswordUpdate(
            code=payload.code,
            password=payload.password,
            email=user.email,
            username=user.username,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=e.errors()
        )

    try:
        updated_user = await crud_user.update_user_password(
            db=db, db_user=user, obj_in=user_in_update
        )
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Не удалось обновить пароль пользователя.",
        )

    await delete_user_sessions(db=db, user=user)
    user_session = await crud_user_session.create_user_session(
        db=db, user=user, request=request, user_agent=user_agent
    )
    logger.info("User %s reset their password successfully", user.username)

    return user_schema.UserUpdatedWithJWT(
        uuid=updated_user.uuid,
        username=updated_user.username,
        email=updated_user.email,
        access_token=await generate_jwt_access_token(user),
        refresh_token=await generate_jwt_refresh_token(user=user, jti=user_session.uuid),
    )

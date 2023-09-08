import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request  # , Body
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app import deps
from app.core.exceptions import (
    PasswordResetCodeInvalid,
    PasswordResetException,
    PasswordResetUserNotFound,
)
from app.core.utils.security import (
    fetch_confirmation_code_data,
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
        raise PasswordResetCodeInvalid()

    logger.debug(
        "User %s is found with code_type: %s", code_data.user_uuid, code_data.code_type
    )

    user = await crud_user.get_by_uuid(db, user_uuid=code_data.user_uuid)
    if not user:
        raise PasswordResetUserNotFound()

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
        raise PasswordResetException()

    await delete_user_sessions(db=db, user=user)
    user_session = await crud_user_session.create_user_session(
        db=db, user=user, request=request, user_agent=user_agent
    )
    logger.info("User %s reset their password successfully", user.username)

    return user_schema.UserUpdatedWithJWT(
        uuid=updated_user.uuid,
        username=updated_user.username,
        email=updated_user.email,
        access_token=await generate_jwt_access_token(user, jti=user_session.uuid),
        refresh_token=await generate_jwt_refresh_token(user=user, jti=user_session.uuid),
    )

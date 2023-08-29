import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException  # , Body
from sqlalchemy.orm import Session

from app import deps
# from app.core.utils import verify_password_reset_token
from app.crud import crud_user
from app.external.exceptions import MonolithUserCreateException
# from app.schemas.response_schema import HTTPResponse
from app.schemas.user_schema import UserUpdate  # , User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/reset")
def reset():
    pass


@router.post("/confirm", status_code=HTTPStatus.CREATED)
async def confirm(payload: UserUpdate, db: Session = Depends(deps.get_db)):
    # email = verify_password_reset_token(token)
    # if not email:
    #     raise HTTPException(
    #         status_code=HTTPStatus.BAD_REQUEST,
    #         detail="Произошла ошибка. Token недействителен!",
    #     )
    email = "tst@kapi.bar"
    user = await crud_user.get_by_email(db, email=email)  # received User
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Произошла ошибка. Такого юзера нет в системе!",
        )
    user_in_update = UserUpdate(password=payload.password)

    try:
        updated_user = await crud_user.update_user_and_sync_to_monolith(
            db=db, db_user=user, obj_in=user_in_update
        )
    except MonolithUserCreateException:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Не удалось обновить пароль пользователя.",
        )

    logger.debug("Password for user %s has been updated successfully", user.username)
    return updated_user

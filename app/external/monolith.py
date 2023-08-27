import requests
from requests import status_codes
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    stop_after_delay,
)

from app.core.settings import settings
from app.external.exceptions import MonolithUserCreateException
from app.models.user import User
from app.schemas.user_schema import UserCreateOnMonolith, UserUpdateOnMonolith


@retry(
    retry=retry_if_not_exception_type(MonolithUserCreateException),
    stop=(stop_after_delay(30) | stop_after_attempt(5)),
)
def update_user_on_monolith(*, user: User):
    update_user_url = f"{settings.monolith_host}/v1/users/"
    updated_user_on_monolith = UserUpdateOnMonolith(
        external_user_uid=user.uuid, password=user.password
    )

    result = requests.post(
        update_user_url,
        headers={
            settings.monolith_internal_token_header: settings.monolith_internal_token
        },
        data=updated_user_on_monolith.model_dump(),
        timeout=10,
    )
    if result.status_code == status_codes.codes.BAD_REQUEST:
        raise MonolithUserCreateException(f"Error {result.content}")
    if not result.ok:
        result.raise_for_status()


@retry(
    retry=retry_if_not_exception_type(MonolithUserCreateException),
    stop=(stop_after_delay(30) | stop_after_attempt(5)),
)
def create_user_on_monolith(*, user: User):
    create_user_url = f"{settings.monolith_host}/v1/users/"
    user_to_monolith = UserCreateOnMonolith(
        external_user_uid=user.uuid,
        username=user.username,
        email=user.email,
    )
    result = requests.post(
        create_user_url,
        headers={
            settings.monolith_internal_token_header: settings.monolith_internal_token
        },
        data=user_to_monolith.model_dump(),
        timeout=10,
    )
    if result.status_code == status_codes.codes.BAD_REQUEST:
        raise MonolithUserCreateException(f"Error {result.content}")
    if not result.ok:
        result.raise_for_status()

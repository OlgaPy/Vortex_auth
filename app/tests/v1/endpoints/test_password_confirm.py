import json
import uuid
from http import HTTPStatus
from unittest import mock

import pytest
# import redis.asyncio as redis
import redis
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.enums import ConfirmationCodeType
from app.core.settings import get_redis_url
from app.core.utils.security import generate_confirmation_code
from app.crud.crud_user import create_user
from app.deps import get_redis
from app.main import app
from app.models.user import User
from app.schemas.user_schema import UserCreate


@pytest.mark.anyio
async def test_password_confirm(db: Session):
    data_create_user = {
        "email": "tst@kapi.bar",
        "username": "testuser",
        "password": "testpass",
    }

    db_user = User(
        username=data_create_user["username"],
        email=data_create_user["email"],
        password=data_create_user["password"],
    )
    db.add(db_user)
    db.commit()

    queried_user = (
        db.query(User).filter(User.email == data_create_user["email"]).first()
    )
    original_password = queried_user.password

    # Fix issue with async
    # Change conftest to pass Redis.
    # Create a function that reads the code from Redis before proceeding further

    redis_client = redis.from_url(get_redis_url())

    code = generate_confirmation_code(
        redis_client, user=db_user, code_type=ConfirmationCodeType.email
    )

    print(code)

    data_update_user_password = {"code": code, "password": "jWe833WkF@5Wv"}

    with mock.patch("app.crud.crud_user.update_user_on_monolith"):  # Rework this once
        async with AsyncClient(app=app, base_url="http://test") as ac:
            result = await ac.post(
                "/v1/password/confirm", json=data_update_user_password
            )

    assert result.status_code == HTTPStatus.CREATED
    response = result.json()

    print(response)

    # assert original_password != response["password"]

    assert False

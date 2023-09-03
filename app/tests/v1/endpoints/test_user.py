import uuid
from http import HTTPStatus
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.utils.security import generate_hashed_password
from app.crud import crud_user
from app.main import app
from app.models.user import User


@pytest.mark.anyio
async def test_register_user(db: Session):
    data = {
        "email": "tst@kapi.bar",
        "username": "testuser",
        "password": "testpass",
    }
    mock_token = mock.AsyncMock(return_value="token")

    with mock.patch("app.crud.crud_user.create_user_on_monolith"), mock.patch.multiple(
        "app.v1.endpoints.user",
        generate_jwt_access_token=mock_token,
        generate_jwt_refresh_token=mock_token,
        generate_and_email_confirmation_code=mock.DEFAULT,
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            result = await ac.post("/v1/user/register", json=data)
    assert result.status_code == HTTPStatus.CREATED
    response = result.json()
    assert response["email"] == data["email"]
    assert response["username"] == data["username"]
    user = await crud_user.get_by_email(db, data["email"])
    assert user.is_active is False


@pytest.mark.parametrize(
    "existing_data,expected_error_message",
    (
        ("username", "Пользователь с таким логином уже зарегистрирован."),
        ("email", "Пользователь с таким email уже зарегистрирован."),
    ),
)
@pytest.mark.anyio
async def test_register_user_with_existing_data(
    db: Session, existing_data, expected_error_message
):
    existing_db_user = User(
        uuid=uuid.uuid4(),
        username="kapibarin",
        email="tst@kapi.bar",
        password=await generate_hashed_password("password"),
    )
    db.add(existing_db_user)
    data = {
        "email": "other@kapi.bar",
        "username": "username",
        "password": "testpass",
        existing_data: getattr(existing_db_user, existing_data),
    }

    mock_token = mock.AsyncMock(return_value="token")

    with mock.patch("app.crud.crud_user.create_user_on_monolith"), mock.patch.multiple(
        "app.v1.endpoints.user",
        generate_jwt_access_token=mock_token,
        generate_jwt_refresh_token=mock_token,
        generate_and_email_confirmation_code=mock.DEFAULT,
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            result = await ac.post("/v1/user/register", json=data)
        assert result.status_code == HTTPStatus.BAD_REQUEST
        response = result.json()
        assert response["detail"] == expected_error_message

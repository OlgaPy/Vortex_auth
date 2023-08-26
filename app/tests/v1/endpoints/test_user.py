from http import HTTPStatus
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.main import app


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
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            result = await ac.post("/v1/user/register", json=data)
    assert result.status_code == HTTPStatus.CREATED
    response = result.json()
    assert response["email"] == data["email"]
    assert response["username"] == data["username"]
    user = await crud_user.get_by_email(db, data["email"])
    assert user.is_active is False

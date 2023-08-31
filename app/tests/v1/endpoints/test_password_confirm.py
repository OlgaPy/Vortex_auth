from http import HTTPStatus
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.utils.security import check_password, create_access_token
from app.crud import crud_user
from app.main import app


@pytest.mark.anyio
async def test_password_confirm(db: Session):
    data_create_user = {
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
            result = await ac.post("/v1/user/register", json=data_create_user)
    assert result.status_code == HTTPStatus.CREATED
    response = result.json()
    assert response["email"] == data_create_user["email"]
    assert response["username"] == data_create_user["username"]
    user = await crud_user.get_by_email(db, data_create_user["email"])
    assert user.is_active is False

    data_update_user_invalid_password = {"password": "newtestpass"}

    with mock.patch("app.crud.crud_user.update_user_on_monolith"), mock.patch.multiple(
        "app.v1.endpoints.password",
        generate_jwt_access_token=mock_token,
        generate_jwt_refresh_token=mock_token,
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/v1/password/confirm", json=data_update_user_invalid_password
            )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    generated_token = create_access_token(data_create_user["email"])

    data_update_user_valid_password = {
        "code": generated_token,
        "password": "jWe833WkF5Wv",
    }

    with mock.patch("app.crud.crud_user.update_user_on_monolith"), mock.patch.multiple(
        "app.v1.endpoints.password",
        generate_jwt_access_token=mock_token,
        generate_jwt_refresh_token=mock_token,
    ):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/v1/password/confirm", json=data_update_user_valid_password
            )

    assert response.status_code == HTTPStatus.CREATED
    res_update_data = response.json()

    assert data_update_user_valid_password["password"] != res_update_data["password"]

    assert check_password(
        data_update_user_valid_password["password"], res_update_data["password"]
    )

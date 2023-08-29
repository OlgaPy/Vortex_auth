from http import HTTPStatus
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.utils import check_password
from app.main import app


@pytest.mark.anyio
async def test_password_confirm(db: Session):
    data_create_user = {
        "email": "tst@kapi.bar",
        "username": "testuser",
        "password": "testpass",
    }
    with mock.patch("app.crud.crud_user.create_user_on_monolith"):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            result = await ac.post("/v1/user/register", json=data_create_user)
    assert result.status_code == HTTPStatus.CREATED
    result_data_create = result.json()
    assert data_create_user["email"] == result_data_create["email"]
    assert data_create_user["username"] == result_data_create["username"]

    data_update_user_invalid_password = {"password": "newtestpass"}

    with mock.patch("app.crud.crud_user.update_user_on_monolith"):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/v1/password/confirm", json=data_update_user_invalid_password
            )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    data_update_user_valid_password = {
        "password": "jWe833WkF5Wv",
    }

    with mock.patch("app.crud.crud_user.update_user_on_monolith"):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/v1/password/confirm", json=data_update_user_valid_password
            )

    assert response.status_code == HTTPStatus.CREATED
    res_update_data = response.json()

    # print(res_update_data)

    assert data_update_user_valid_password["password"] != res_update_data["password"]

    assert check_password(
        data_update_user_valid_password["password"], res_update_data["password"]
    )

    # assert False

from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.utils.security import decode_token
from app.main import app
from app.models.user import User
from app.tests.data import TestUser


@pytest.mark.anyio
class TestLoginUser:
    @pytest.mark.parametrize(
        "username,password,expected_status_code",
        (
            (TestUser.username, TestUser.password, HTTPStatus.OK),
            (TestUser.username, "wrongpassword", HTTPStatus.UNAUTHORIZED),
            (TestUser.email, TestUser.password, HTTPStatus.OK),
            (TestUser.email, "wrongpassword", HTTPStatus.UNAUTHORIZED),
            ("wrongusername", TestUser.password, HTTPStatus.UNAUTHORIZED),
            ("wrongemail@example.com", TestUser.password, HTTPStatus.UNAUTHORIZED),
            ("", TestUser.password, HTTPStatus.UNAUTHORIZED),
            (TestUser.email, "", HTTPStatus.UNAUTHORIZED),
            ("", "", HTTPStatus.UNAUTHORIZED),
        ),
    )
    @pytest.mark.parametrize("user_is_active", (True, False))
    async def test_login_user(
        self,
        user_is_active,
        username,
        password,
        expected_status_code,
        db: Session,
        user: User,
    ):
        user.is_active = user_is_active
        db.commit()

        result = await self._login({"username": username, "password": password})

        assert result.status_code == expected_status_code
        response = result.json()
        if expected_status_code != HTTPStatus.OK:
            assert (
                response["detail"] == "Пользователь с таким данными не зарегистрирован."
            )
            return
        assert len(user.sessions) == 1
        assert response["uuid"] == str(user.uuid)
        assert response["username"] == user.username
        assert response["email"] == user.email

        access_token = await decode_token(response["access_token"])
        refresh_token = await decode_token(response["refresh_token"])

        assert access_token["token_type"] == "access"
        assert access_token["user_id"] == str(user.uuid)
        assert access_token["is_active"] == user.is_active

        assert refresh_token["token_type"] == "refresh"
        assert refresh_token["user_id"] == str(user.uuid)
        assert refresh_token["jti"] == str(user.sessions[0].uuid)

    async def _login(self, data: dict):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.post("/v1/user/login", json=data)

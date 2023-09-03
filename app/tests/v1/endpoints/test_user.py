import uuid
from http import HTTPStatus
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.utils.security import check_password, generate_hashed_password
from app.crud import crud_user
from app.main import app
from app.models.user import User


@pytest.mark.anyio
class TestUSer:
    def setup(self):
        self.user_data = dict(
            email="tst@example.com",
            username="testuser",
            password="testpass",
        )
        self.mock_token = mock.AsyncMock(return_value="token")
        self.patch_externals = mock.patch.multiple(
            "app.v1.endpoints.user",
            generate_jwt_access_token=self.mock_token,
            generate_jwt_refresh_token=self.mock_token,
            generate_and_email_confirmation_code=mock.DEFAULT,
        )
        self.patch_create_user = mock.patch("app.crud.crud_user.create_user_on_monolith")

    async def test_register_user(self, db: Session):
        with self.patch_create_user, self.patch_externals:
            result = await self._register(self.user_data)

        assert result.status_code == HTTPStatus.CREATED
        response = result.json()
        assert response["email"] == self.user_data["email"]
        assert response["username"] == self.user_data["username"]
        assert response["access_token"] == await self.mock_token()
        assert response["refresh_token"] == await self.mock_token()
        user = await crud_user.get_by_email(db, self.user_data["email"])
        assert user.is_active is False
        assert check_password(self.user_data["password"], user.password) is True
        assert len(user.sessions) == 1

    @pytest.mark.parametrize(
        "username",
        (
            "   sh      ",
            "veryyyloooonguuusername",
            "wrong!chars",
            " admin ",
            "moder ",
            " moderator",
        ),
    )
    async def test_register_user_invalid_username(self, db: Session, username):
        with self.patch_create_user, self.patch_externals:
            result = await self._register({**self.user_data, "username": username})

        assert (
            result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ), result.content.decode()

    @pytest.mark.parametrize(
        "existing_data,expected_error_message",
        (
            ("username", "Пользователь с таким логином уже зарегистрирован."),
            ("email", "Пользователь с таким email уже зарегистрирован."),
        ),
    )
    async def test_register_user_with_existing_data(
        self, db: Session, existing_data, expected_error_message
    ):
        existing_db_user = User(
            uuid=uuid.uuid4(),
            username="newuser",
            email="tst@example.com",
            password=await generate_hashed_password("password"),
        )
        db.add(existing_db_user)
        data = {
            "email": "other@example.com",
            "username": "username",
            "password": "testpass",
            existing_data: getattr(existing_db_user, existing_data),
        }
        with self.patch_create_user, self.patch_externals:
            result = await self._register(data)

        assert result.status_code == HTTPStatus.BAD_REQUEST
        response = result.json()
        assert response["detail"] == expected_error_message

    async def test_register_user_monolith_not_responding(self, db: Session):
        with mock.patch(
            "app.crud.crud_user.create_user_on_monolith",
            side_effect=Exception("From test"),
        ), self.patch_externals:
            result = await self._register(self.user_data)
        assert result.status_code == HTTPStatus.BAD_GATEWAY
        response = result.json()
        assert response["detail"] == "Не удалось зарегистрировать пользователя."
        user = await crud_user.get_by_email(db, self.user_data["email"])
        assert user is None

    @pytest.mark.parametrize("email", ("hello@", "@hello", "admin@kapi.bar"))
    async def test_register_user_wrong_email(self, db: Session, email):
        with self.patch_create_user, self.patch_externals:
            result = await self._register({**self.user_data, "email": email})

        assert (
            result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ), result.content.decode()

    async def _register(self, data: dict):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.post("/v1/user/register", json=data)

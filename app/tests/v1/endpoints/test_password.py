from http import HTTPStatus
from unittest import mock

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.enums import ConfirmationCodeType
from app.main import app
from app.models.user import User, UserSession
from app.schemas.security_schema import ConfirmationCodeData


@pytest.mark.anyio
class TestPassword:
    def setup_method(self):
        self.mock_access_token = mock.AsyncMock(return_value="access token")
        self.mock_refresh_token = mock.AsyncMock(return_value="refresh token")
        self.patch_external = mock.patch.multiple(
            "app.v1.endpoints.password",
            generate_jwt_access_token=self.mock_access_token,
            generate_jwt_refresh_token=self.mock_refresh_token,
        )
        self.mock_fetch_confirmation_code_data = mock.patch(
            "app.v1.endpoints.password.fetch_confirmation_code_data"
        )

    @pytest.mark.parametrize(
        "password,expected_error_type",
        (
            ("     sh     ", "short_password"),
            ("passwordnocapital!12", "password_no_capital"),
            ("Passwordnospecial12", "password_no_specialchars"),
            ("Passwordnodigit!", "password_no_digits"),
            ("PASSWORDNOSMALL!12", "password_no_lowercase"),
            ("Testuser1!", "password_similar"),
        ),
    )
    async def test_password_invalid(
        self, db: Session, password, expected_error_type, user: User
    ):
        initial_user_password_hash = user.password
        with (
            self.mock_fetch_confirmation_code_data as mock_fetch_confirmation_code_data,
            self.patch_external,
        ):
            mock_fetch_confirmation_code_data.return_value = ConfirmationCodeData(
                user_uuid=user.uuid, code_type=ConfirmationCodeType.email
            )
            result = await self._password_confirm(
                {
                    "code": "code",
                    "password": password,
                }
            )

        assert (
            result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        ), result.content.decode()
        response = result.json()
        error_type = response["detail"][0]["type"]
        assert error_type == expected_error_type, response
        assert user.password == initial_user_password_hash

    @pytest.mark.parametrize(
        ("code_expired", "password", "response_expected_status_code"),
        (
            (
                False,
                "jWe833WkF@5W",
                HTTPStatus.CREATED,
            ),
            (
                True,
                "jWe833WkF@5W",
                HTTPStatus.BAD_REQUEST,
            ),
        ),
    )
    async def test_password_confirm(
        self,
        db: Session,
        code_expired,
        password,
        response_expected_status_code,
        user: User,
    ):
        initial_user_password_hash = user.password
        with (
            self.mock_fetch_confirmation_code_data as mock_fetch_confirmation_code_data,
            self.patch_external,
        ):
            if code_expired:
                mock_fetch_confirmation_code_data.return_value = None
            else:
                mock_fetch_confirmation_code_data.return_value = ConfirmationCodeData(
                    user_uuid=user.uuid, code_type=ConfirmationCodeType.email
                )

            result = await self._password_confirm(
                {
                    "code": "code",
                    "password": password,
                }
            )

        assert (
            result.status_code == response_expected_status_code
        ), result.content.decode()

        if response_expected_status_code == HTTPStatus.CREATED:
            response = result.json()
            assert user.password != initial_user_password_hash
            assert response["access_token"] == await self.mock_access_token()
            assert response["refresh_token"] == await self.mock_refresh_token()
        else:
            assert user.password == initial_user_password_hash

    async def test_user_sessions_are_deleted(self, db, user: User):
        first_session = UserSession(user=user, ip="127.0.0.1", useragent="Test UA")
        db.add(first_session)
        db.commit()
        second_session = UserSession(user=user, ip="127.0.0.1", useragent="Test UA")
        db.add(second_session)
        db.commit()
        old_session_uuids = [first_session.uuid, second_session.uuid]

        with (
            self.mock_fetch_confirmation_code_data as mock_fetch_confirmation_code_data,
            self.patch_external,
        ):
            mock_fetch_confirmation_code_data.return_value = ConfirmationCodeData(
                user_uuid=user.uuid, code_type=ConfirmationCodeType.email
            )

            result = await self._password_confirm(
                {
                    "code": "code",
                    "password": "SuperStrongPassword1234!",
                }
            )

        assert result.status_code == HTTPStatus.CREATED, result.content.decode()

        assert len(user.sessions) == 1
        assert user.sessions[0].uuid not in old_session_uuids

    async def _password_confirm(self, data: dict):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.post("/v1/password/confirm", json=data)

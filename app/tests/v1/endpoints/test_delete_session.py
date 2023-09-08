import datetime
import uuid
from http import HTTPStatus

import jwt
import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.enums import TokenType
from app.core.settings import settings
from app.main import app
from app.models.user import User, UserSession


@pytest.mark.anyio
class TestDeleteSession:
    @pytest.mark.parametrize(
        "except_current,expected_sessions_count",
        (
            (True, 1),
            (False, 0),
            ("true", 1),
            ("false", 0),
            (1, 1),
            (0, 0),
        ),
    )
    async def test_delete_sessions(
        self, db: Session, except_current, expected_sessions_count, access_token_and_user
    ):
        access_token, user = access_token_and_user
        current_session_uuid = user.sessions[0].uuid
        first_session = UserSession(user=user, ip="127.0.0.1", useragent="Test UA")
        db.add(first_session)
        db.commit()
        second_session = UserSession(user=user, ip="127.0.0.1", useragent="Test UA")
        db.add(second_session)
        db.commit()

        # Create another user in order to check if we don't delete their sessions
        another_user = User(
            username="testusername", email="email@example.com", password="password"
        )
        db.add(another_user)
        db.commit()
        db.add(UserSession(user=another_user, ip="127.0.0.1", useragent="Test UA"))
        db.commit()

        assert len(user.sessions) == 3
        assert len(another_user.sessions) == 1
        result = await self._delete_sessions(
            params={"except_current": except_current},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert result.status_code == HTTPStatus.NO_CONTENT
        assert len(user.sessions) == expected_sessions_count
        assert len(another_user.sessions) == 1
        if expected_sessions_count == 1:
            assert user.sessions[0].uuid == current_session_uuid

    async def test_delete_sessions_wrong_token(self, refresh_token):
        result = await self._delete_sessions(
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert result.status_code == HTTPStatus.BAD_REQUEST
        response = result.json()
        assert response["detail"][0]["type"] == "wrong_token_type"

    async def test_delete_sessions_expired_token(self, access_token_and_user):
        access_token, _ = access_token_and_user
        with freeze_time(
            datetime.datetime.now()
            + datetime.timedelta(minutes=settings.jwt_access_token_lifetime_minutes + 1)
        ):
            result = await self._delete_sessions(
                headers={"Authorization": f"Bearer {access_token}"}
            )
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == "token_expired"

    async def test_delete_sessions_without_bearer(self):
        result = await self._delete_sessions(headers={})
        assert result.status_code == HTTPStatus.FORBIDDEN
        response = result.json()
        assert response["detail"][0]["type"] == "forbidden"

    @pytest.mark.parametrize("jti", (None, "wrong", uuid.uuid4()))
    @pytest.mark.parametrize("user_id", (None, "random", uuid.uuid4()))
    async def test_delete_sessions_without_user_in_db(self, db, user_id, jti):
        token = dict(
            exp=datetime.datetime.now()
            + datetime.timedelta(days=settings.jwt_refresh_token_lifetime_days),
            iss=settings.jwt_issuer,
            aud=settings.jwt_audience,
            token_type=TokenType.access,
        )
        if user_id:
            token["user_id"] = str(user_id)
        if jti:
            token["jti"] = str(jti)

        access_token = jwt.encode(
            payload=token,
            key=settings.jwt_rsa_private_key,
            algorithm=settings.jwt_algorithm,
        )
        result = await self._delete_sessions(
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] in ("token_invalid", "user_not_found")

    @pytest.mark.parametrize(
        "auth_header,expected_error_type,expected_status_code",
        (
            ("Bearer test", "token_invalid", HTTPStatus.UNAUTHORIZED),
            ("just content", "forbidden", HTTPStatus.FORBIDDEN),
        ),
    )
    async def test_delete_sessions_wrong_auth_header(
        self, auth_header, expected_error_type, expected_status_code
    ):
        result = await self._delete_sessions(headers={"Authorization": auth_header})
        assert result.status_code == expected_status_code
        response = result.json()
        assert response["detail"][0]["type"] == expected_error_type

    async def _delete_sessions(self, headers: dict, params: dict = None):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.delete("/v1/session/", params=params, headers=headers)

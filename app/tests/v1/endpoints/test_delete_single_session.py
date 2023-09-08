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
class TestDeleteSingleSession:
    async def test_delete_single_session(self, db: Session, access_token_and_user):
        access_token, user = access_token_and_user
        another_session = UserSession(user=user, ip="127.0.0.1", useragent="Test UA")
        db.add(another_session)
        db.commit()

        assert len(user.sessions) == 2
        result = await self._delete_session(
            str(another_session.uuid),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert result.status_code == HTTPStatus.NO_CONTENT
        assert len(user.sessions) == 1

    async def test_delete_single_session_not_existing(self, access_token_and_user):
        access_token, user = access_token_and_user

        result = await self._delete_session(
            str(uuid.uuid4()), headers={"Authorization": f"Bearer {access_token}"}
        )
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert len(user.sessions) == 1
        response = result.json()
        assert response["detail"][0]["type"] == "not_found"

    async def test_cannot_delete_other_user_session(
        self, db: Session, access_token_and_user
    ):
        access_token, original_user = access_token_and_user

        another_user = User(
            username="username",
            email="email@example.com",
            password="password",
        )
        db.add(another_user)
        db.commit()

        another_user_session = UserSession(
            user=another_user, ip="127.0.0.1", useragent="Test UA"
        )
        db.add(another_user_session)
        db.commit()

        result = await self._delete_session(
            str(another_user_session.uuid),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert len(original_user.sessions) == 1
        assert len(another_user.sessions) == 1

        response = result.json()
        assert response["detail"][0]["type"] == "not_found"

    async def test_delete_single_session_wrong_token(self, refresh_token):
        result = await self._delete_session(
            str(uuid.uuid4()), headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert result.status_code == HTTPStatus.BAD_REQUEST
        response = result.json()
        assert response["detail"][0]["type"] == "wrong_token_type"

    async def test_delete_single_sessions_expired_token(self, access_token_and_user):
        access_token, _ = access_token_and_user
        with freeze_time(
            datetime.datetime.now()
            + datetime.timedelta(minutes=settings.jwt_access_token_lifetime_minutes + 1)
        ):
            result = await self._delete_session(
                str(uuid.uuid4()), headers={"Authorization": f"Bearer {access_token}"}
            )
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == "token_expired"

    async def test_delete_single_session_without_bearer(self):
        result = await self._delete_session(str(uuid.uuid4()), headers={})
        assert result.status_code == HTTPStatus.FORBIDDEN
        response = result.json()
        assert response["detail"][0]["type"] == "forbidden"

    @pytest.mark.parametrize("jti", (None, "wrong", uuid.uuid4()))
    @pytest.mark.parametrize("user_id", (None, "random", uuid.uuid4()))
    async def test_delete_single_session_without_user_in_db(self, db, user_id, jti):
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
        result = await self._delete_session(
            str(uuid.uuid4()), headers={"Authorization": f"Bearer {access_token}"}
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
    async def test_delete_single_session_wrong_auth_header(
        self, auth_header, expected_error_type, expected_status_code
    ):
        result = await self._delete_session(
            str(uuid.uuid4()), headers={"Authorization": auth_header}
        )
        assert result.status_code == expected_status_code
        response = result.json()
        assert response["detail"][0]["type"] == expected_error_type

    async def _delete_session(self, session_uuid: str, headers: dict):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.delete(f"/v1/session/{session_uuid}", headers=headers)

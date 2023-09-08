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
from app.models.user import UserSession


@pytest.mark.anyio
class TestSession:
    async def test_list_sessions(self, db: Session, access_token):
        result = await self._get_sessions(
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert result.status_code == HTTPStatus.OK
        response = result.json()
        assert len(response) == 1
        session = db.query(UserSession).first()
        assert response[0]["uuid"] == str(session.uuid)

    async def test_list_sessions_wrong_token(self, refresh_token):
        result = await self._get_sessions(
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert result.status_code == HTTPStatus.BAD_REQUEST
        response = result.json()
        assert response["detail"][0]["type"] == "wrong_token_type"

    async def test_list_sessions_expired_token(self, access_token):
        with freeze_time(
            datetime.datetime.now()
            + datetime.timedelta(minutes=settings.jwt_access_token_lifetime_minutes + 1)
        ):
            result = await self._get_sessions(
                headers={"Authorization": f"Bearer {access_token}"}
            )
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == "token_expired"

    async def test_list_sessions_without_bearer(self):
        result = await self._get_sessions(headers={})
        assert result.status_code == HTTPStatus.FORBIDDEN
        response = result.json()
        assert response["detail"][0]["type"] == "forbidden"

    @pytest.mark.parametrize("jti", (None, "wrong", uuid.uuid4()))
    @pytest.mark.parametrize("user_id", (None, "random", uuid.uuid4()))
    async def test_list_sessions_without_user_in_db(self, user_id, jti):
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
        result = await self._get_sessions(
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
    async def test_list_sessions_wrong_auth_header(
        self, auth_header, expected_error_type, expected_status_code
    ):
        result = await self._get_sessions(headers={"Authorization": auth_header})
        assert result.status_code == expected_status_code
        response = result.json()
        assert response["detail"][0]["type"] == expected_error_type

    async def _get_sessions(self, headers: dict):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.get("/v1/session/", headers=headers)

import datetime
import uuid
from http import HTTPStatus

import jwt
import pytest
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.utils.security import generate_jwt_refresh_token
from app.main import app
from app.models.user import User, UserSession


@pytest.mark.anyio
class TestRefreshToken:
    async def test_token_refreshed(self, db: Session, refresh_token: str):
        token_refresh_timestamp = datetime.datetime.now() + datetime.timedelta(
            days=settings.jwt_refresh_token_lifetime_days - 1
        )
        with freeze_time(token_refresh_timestamp):
            result = await self._refresh_token(data={"refresh_token": refresh_token})

        user_session = db.query(UserSession).first()
        assert result.status_code == HTTPStatus.CREATED
        response = result.json()
        assert response["refresh_token"] == refresh_token
        assert user_session.last_activity == token_refresh_timestamp

    async def test_cannot_be_refreshed_with_wrong_token_type(self, access_token: str):
        result = await self._refresh_token(data={"refresh_token": access_token})
        assert result.status_code == HTTPStatus.BAD_REQUEST
        response = result.json()
        assert response["detail"][0]["type"] == "wrong_token_type", response

    async def test_cannot_be_refreshed_with_expired_token(self, refresh_token: str):
        with freeze_time(
            datetime.datetime.now()
            + datetime.timedelta(days=settings.jwt_refresh_token_lifetime_days + 1)
        ):
            result = await self._refresh_token(data={"refresh_token": refresh_token})
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == "token_expired", response

    async def test_cannot_be_refreshed_with_wrong_format_token(self):
        result = await self._refresh_token(
            data={"refresh_token": jwt.encode({"some": "token"}, "secret")}
        )
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == "token_invalid"

    async def test_cannot_be_refreshed_without_user_session(self, user: User):
        refresh_token = await generate_jwt_refresh_token(user=user, jti=str(uuid.uuid4()))
        result = await self._refresh_token(data={"refresh_token": refresh_token})
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == "session_from_token_not_found"

    @pytest.mark.parametrize("jti", (None, "wrong"))
    async def test_cannot_be_refreshed_with_wrong_user_session_info(
        self, jti, user: User
    ):
        token = dict(
            exp=datetime.datetime.now()
            + datetime.timedelta(days=settings.jwt_refresh_token_lifetime_days),
            iss=settings.jwt_issuer,
            aud=settings.jwt_audience,
            user_id=str(user.uuid),
            token_type="refresh",
        )
        if jti:
            token["jti"] = jti

        refresh_token = jwt.encode(
            payload=token,
            key=settings.jwt_rsa_private_key,
            algorithm=settings.jwt_algorithm,
        )

        result = await self._refresh_token(data={"refresh_token": refresh_token})
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        response = result.json()
        assert response["detail"][0]["type"] == (
            "session_from_token_not_found" if jti else "token_invalid"
        )

    async def _refresh_token(self, data: dict):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            return await ac.post("/v1/token/refresh", json=data)

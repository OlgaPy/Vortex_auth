from datetime import datetime
from secrets import token_hex

import jwt
import sqlalchemy as sa
from sqlalchemy.orm import Session as DbSession

from models import errors
from models.users import Session, Solt, TokenPayload, User
from tools.passwords import password_hash


class AuthService:
    """Сервис авторизации."""

    def __init__(self, session: DbSession):
        self._db = session

    def check_password(self, user: User, password: str) -> bool:
        """Проверка совпадения пароля с паролем пользователя."""

        solt = self._db.get(Solt, user.id)
        return user.password == password_hash(password, solt.solt)

    def login(self, login: str, password: str) -> Session:
        """Логин пользователя и получение токена доступа."""

        query = sa.select(User).where(User.login == login)
        user: User = self._db.execute(query).scalar_one_or_none()
        if user is None:
            raise errors.UserNotFound(f"no user with login: {login}")

        if not self.check_password(user, password):
            raise errors.Forbidden

        sid = token_hex(32)
        token_payload = TokenPayload(
            sid=sid, user_id=user.id, username=user.login, access=user.access
        )

        token = jwt.encode({"payload": token_payload}, "kapibara", algorithm="HS256")
        session = Session(
            sid=sid,
            # user=user,
            user_id=user.id,
            token=token,
            refresh_token=token_hex(32),
            created_at=datetime.now(),
        )
        self._db.add(session)
        self._db.commit()

        return session

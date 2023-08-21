from datetime import datetime

# from hashlib import md5
from secrets import token_hex

# import jwt
# import sqlalchemy as sa
from sqlalchemy.orm import Session as DbSession

# from models import User, errors
from models.users import Solt, User  # , TokenPayload, Session
from tools.passwords import password_hash


class UserService:
    """Сервис управления пользователями."""

    def __init__(self, session: DbSession):
        self._db = session

    def create_user(self, login: str, password: str) -> User:
        """Создание нового пользователя."""

        solt_str = token_hex(8)

        user = User(
            id=token_hex(32),
            login=login,
            password=password_hash(password, solt_str),
            created_at=datetime.now(),
        )

        solt = Solt(user_id=user.id, solt=solt_str)

        self._db.add(user)
        self._db.flush()
        self._db.add(solt)

        self._db.commit()

        return user

    def get_user(self, user_id: str) -> User:
        """Получение пользователя по id."""

        raise NotImplementedError

    def get_users(self, page: int) -> list[User]:
        """Получение пользователя по id."""

        raise NotImplementedError

    def edit_user(self, login: str, password: str, email: str) -> User:
        """Редактирование пользователя."""

        raise NotImplementedError

    def delete_user(self, user_id: str) -> User:
        """Удаление пользователя."""

        raise NotImplementedError

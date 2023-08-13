from models import User
from hashlib import md5
from datetime import datetime
import jwt

from sqlalchemy.orm import Session as DbSession
import sqlalchemy as sa

from models.users import User, Solt, Session, TokenPayload
from models import errors
from tools.passwords import password_hash
from secrets import token_hex


class UserService:
    """Сервис управления пользователями"""

    def __init__(self, session: DbSession):
        self._db = session

    def create_user(self, login: str, password: str) -> User:
        """Создание нового пользователя"""

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
        """Получение пользователя по id"""

        raise NotImplemented

    def get_users(self, page: int) -> list[User]:
        """Получение пользователя по id"""

        raise NotImplemented

    def edit_user(self, login: str, password: str, email: str) -> User:
        """Редактирование пользователя"""

        raise NotImplemented

    def delete_user(self, user_id: str) -> User:
        """Удаление пользователя"""

        raise NotImplemented

from datetime import datetime
from typing import TypedDict

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

__all__ = ['Table', 'User', 'Solt', 'Session', 'TokenPayload']


class Table(DeclarativeBase):
    """Таблица"""


class User(Table):
    """Модель пользователя"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(sa.String(64), primary_key=True)
    login: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    access: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)


class Solt(Table):
    """Соль для хеширования паролей"""

    __tablename__ = "solt"

    user_id: Mapped[str] = mapped_column(sa.ForeignKey("users.id", ondelete="cascade"), primary_key=True)
    solt: Mapped[str] = mapped_column(sa.String(16), nullable=False)


class Session(Table):
    """Модель сессии"""

    __tablename__ = "sessions"

    sid: Mapped[str] = mapped_column(sa.String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(sa.ForeignKey("users.id", ondelete="cascade"))
    # user: Mapped[User] = relationship("User", back_populates="users")
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)
    token: Mapped[str] = mapped_column(sa.Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(sa.String(64), nullable=False)


class TokenPayload(TypedDict):
    """Полезная нагрузка токена"""

    sid: str
    user_id: str
    username: str
    access: int

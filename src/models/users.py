from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase as Base,
    Mapped,
    mapped_column,
    relationship
)


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(sa.UUID, primary_key=True)
    login: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    deleted_at: Mapped[datetime]


class Session(Base):
    """Модель сессии"""

    sid: Mapped[str] = mapped_column(sa.UUID, primary_key=True)
    user: Mapped[User] = relationship(back_populates="users")

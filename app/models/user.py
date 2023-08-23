import uuid
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import BaseTable


class User(BaseTable):
    """User information."""

    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(
        sa.String(64), nullable=False, unique=True, index=True
    )
    email: Mapped[EmailStr] = mapped_column(
        sa.String(255), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    email_activated_at: Mapped[datetime] = mapped_column(nullable=True)
    telegram_activated_at: Mapped[datetime] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_onupdate=sa.func.now()
    )
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)


"""
from app.models.user import User
from app.db.session import SessionLocal
user = User(username="test", password="psd", email="test@email.com")
session = SessionLocal()
session.add(user)
session.commit()

"""

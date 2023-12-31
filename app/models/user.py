import uuid
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from pydantic import EmailStr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import BaseTable


class User(BaseTable):
    """User information."""

    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, unique=True, index=True
    )
    email: Mapped[EmailStr] = mapped_column(
        sa.String(255), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(sa.String(72), nullable=False)
    email_activated_at: Mapped[datetime] = mapped_column(nullable=True)
    telegram_activated_at: Mapped[datetime] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=True, server_onupdate=sa.func.now()
    )
    synced_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user")


class UserSession(BaseTable):
    """Store user session with various details."""

    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_uuid: Mapped[UUID] = mapped_column(sa.ForeignKey("user.uuid"))
    user: Mapped["User"] = relationship(back_populates="sessions")
    ip: Mapped[str] = mapped_column(sa.String(15), nullable=False)
    useragent: Mapped[str] = mapped_column(sa.Text(), nullable=True)
    last_activity: Mapped[datetime] = mapped_column(
        nullable=False, server_default=sa.func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=sa.func.now()
    )

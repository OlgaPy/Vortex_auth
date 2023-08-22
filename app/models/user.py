from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import BaseTable


class User(BaseTable):
    """User information."""

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(sa.String(64), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    access: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(nullable=True)

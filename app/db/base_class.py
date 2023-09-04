import uuid

from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class GUID(TypeDecorator):
    """Postgres realization of UUID field."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(UUID())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class BaseTable(DeclarativeBase):
    """Base model to inherit from."""

    type_annotation_map = {
        uuid.UUID: GUID,
    }
    __name__: str  # noqa: VNE003

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

"""Инъекторы подключений (БД)"""

from sqlalchemy import create_engine, URL, Connection
from sqlalchemy.orm import DeclarativeBase, Session

from models.users import Table


def make_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        host="db",
        port=5432,
        username="postgres",
        password="postgres",
        database="auth"
    )
    return create_engine(url)


# TODO: сделать правильный менеджмент подключениями
class ConnectionManager:

    INSTANCE: 'ConnectionManager' = None

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            cls.INSTANCE = super().__new__(cls, *args, **kwargs)
        return cls.INSTANCE

    def __init__(self):
        self._engine = make_engine()
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session:
            return self._session
        return Session(self._engine)


def init_tables():
    engine = make_engine()
    Table.registry.configure()
    Table.registry.metadata.create_all(engine)

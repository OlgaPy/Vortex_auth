from typing import Generator
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from app.core.settings import settings
from app.core.utils.security import generate_hashed_password
from app.db.base_class import BaseTable
from app.deps import get_db, get_redis
from app.main import app
from app.models.user import User


@pytest.fixture
def anyio_backend():
    """Make async tests to be executed against asyncio backend, another option is trio.

    Delete this fixture if every test needs to be executed against both backends.
    """
    return "asyncio"


@pytest.fixture
def anyio_backend():
    """Make async tests to be executed against asyncio backend, another option is trio.

    Delete this fixture if every test needs to be executed against both backends.
    """
    return "asyncio"


@pytest.fixture(scope="session")
def db_engine() -> Generator:
    test_db_url = str(
        PostgresDsn.build(
            scheme="postgresql",
            username=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_server,
            path="test",
        )
    )
    if not database_exists(test_db_url):
        create_database(test_db_url)
    test_engine = create_engine(test_db_url, pool_pre_ping=True)
    BaseTable.metadata.create_all(bind=test_engine)

    yield test_engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection)
    app.dependency_overrides[get_db] = lambda: db

    yield db

    db.close()
    transaction.rollback()
    connection.close()


async def redis_mock():
    return mock.AsyncMock()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c


app.dependency_overrides[get_redis] = redis_mock


@pytest.fixture
async def user(db):
    db_user = User(
        username="testuser",
        email="testuser@example.com",
        password=await generate_hashed_password("password"),
    )
    db.add(db_user)
    db.commit()
    return db_user

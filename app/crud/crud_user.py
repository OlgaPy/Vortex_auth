import datetime
import uuid

from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.utils import generate_hashed_password
from app.external.monolith import create_user_on_monolith
from app.models.user import User
from app.schemas import user_schema


async def create_user(db: Session, user: user_schema.UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def create_user_and_sync_to_monolith(
    *, db: Session, user: user_schema.UserCreate
) -> User:
    db_user = User(
        uuid=uuid.uuid4(),
        username=user.username,
        email=user.email,
        password=generate_hashed_password(user.password),
    )
    db.add(db_user)
    try:
        create_user_on_monolith(user=db_user)
        db_user.synced_at = datetime.datetime.now()
    except Exception:
        db.rollback()
        raise
    db.commit()
    return db_user


async def get_by_email(db: Session, email: EmailStr) -> User | None:
    return db.query(User).filter(User.email == email).first()


async def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

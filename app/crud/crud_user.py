import datetime
import logging
import uuid
from typing import Any, Dict, Union

from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.utils import generate_hashed_password
from app.external.monolith import create_user_on_monolith, update_user_on_monolith
from app.models.user import User
from app.schemas import user_schema

logger = logging.getLogger(__name__)


async def update_user_and_sync_to_monolith(
        db: Session, db_user: User, obj_in: Union[user_schema.UserUpdate, Dict[str, Any]]
) -> User | None:
    """
    Will update User in DB. Mostly reserved for the pass.
    """
    obj_data = jsonable_encoder(db_user)
    if isinstance(obj_in, dict):
        updated_data = obj_in
    else:
        updated_data = obj_in.model_dump(exclude_unset=True)  # To receive partial updates
    if updated_data["password"]:
        hashed_password = generate_hashed_password(updated_data["password"])
        del updated_data["password"]
        updated_data["password"] = hashed_password
    for field in obj_data:
        if field in updated_data:
            setattr(db_user, field, updated_data[field])

    db.add(db_user)
    try:
        update_user_on_monolith(user=db_user)
        db_user.synced_at = datetime.datetime.now()
    except Exception:
        db.rollback()
        logger.exception("Can't updated user %s on monolith", db_user.username)
        raise
    logger.info("User %s synced to the monolith", db_user.username)
    db.commit()
    db.refresh(db_user)
    return db_user


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

import uuid
from typing import Type

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.user import User, UserSession


async def create_user_session(
    *, db: Session, user: User, request: Request, user_agent: str | None
) -> UserSession:
    user_session = UserSession(user=user, ip=request.client.host, useragent=user_agent)
    db.add(user_session)
    db.commit()
    return user_session


async def delete_user_sessions(
    *, db: Session, user: User, exclude_uuids: list[uuid.UUID | str] = None
) -> None:
    query = db.query(UserSession).filter(UserSession.user == user)
    if exclude_uuids:
        query = query.filter(UserSession.uuid.notin_(exclude_uuids))
    query.delete()
    db.commit()


async def delete_user_session(
    *, db: Session, user: User, user_session_uuid: str | uuid.UUID
) -> bool:
    query = db.query(UserSession).filter(
        UserSession.user == user, UserSession.uuid == user_session_uuid
    )
    result = query.delete()
    db.commit()
    return bool(result)


async def get_user_sessions_by_user_uuid(
    db: Session, user_uuid: str | uuid.UUID
) -> list[Type[UserSession]] | None:
    return db.query(UserSession).filter(UserSession.user_uuid == user_uuid).all()


async def get_user_session_by_uuid(
    db: Session, user_session_uuid: str | uuid.UUID
) -> UserSession | None:
    return db.query(UserSession).filter(UserSession.uuid == user_session_uuid).first()

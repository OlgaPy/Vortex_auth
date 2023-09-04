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


async def get_user_sessions_by_user_uuid(
    db: Session, user_uuid
) -> list[Type[UserSession]] | None:
    return db.query(UserSession).filter(UserSession.user_uuid == user_uuid).all()

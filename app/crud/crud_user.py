from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas import user


def create_user(db: Session, user: user.UserCreate):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

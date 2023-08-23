from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import deps
from app.crud import crud_user
from app.schemas import user

router = APIRouter()


@router.post("/register", response_model=user.User)
def register(user: user.UserCreate, db: Session = Depends(deps.get_db)):
    return crud_user.create_user(db, user)


@router.post("/login")
def login():
    ...

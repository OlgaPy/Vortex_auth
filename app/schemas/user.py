import uuid

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base model for User entry."""

    email: EmailStr | None = None


class UserCreate(UserBase):
    """Model to create user."""

    email: EmailStr
    username: str
    password: str


class UserUpdate(UserBase):
    """Model to update user."""

    password: str


class UserInDbBase(UserBase):
    """Base model for database representation of a user."""

    uuid: uuid.UUID

    class Config:
        from_attributes = True


class User(UserInDbBase):
    """User database model."""

    username: str
    email: str

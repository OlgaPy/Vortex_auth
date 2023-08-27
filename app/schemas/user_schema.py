import uuid

from pydantic import BaseModel, EmailStr, constr, field_validator
from pydantic_core.core_schema import FieldValidationInfo

UsernameStr = constr(
    strip_whitespace=True, min_length=4, max_length=16, pattern=r"^[a-zA-Z0-9.\-_]+$"
)


class UserBase(BaseModel):
    """Base model for User entry."""

    email: EmailStr | None = None


class UserCreate(UserBase):
    """Model to create user."""

    email: EmailStr
    username: UsernameStr
    password: str

    @field_validator("username")
    @classmethod
    def check_username(cls, value: str, info: FieldValidationInfo) -> str:
        # TODO: добавить проверку по словарю
        # assert False, f"{info.field_name} Такое имя запрещено к регистрации"
        return value


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


class UserCreateOnMonolith(BaseModel):
    """Data to be sent to monolith."""

    external_user_uid: uuid.UUID
    username: UsernameStr
    email: EmailStr


class UserUpdateOnMonolith(BaseModel):
    """Updated data to be sent to monolith."""

    external_user_uid: uuid.UUID
    password: str

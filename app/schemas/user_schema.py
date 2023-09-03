import re
import uuid
from difflib import SequenceMatcher

from pydantic import BaseModel, ConfigDict, EmailStr, constr, field_validator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import FieldValidationInfo

from app.core.settings import settings
from app.core.utils.security import is_username_allowed_to_register

UsernameStr = constr(strip_whitespace=True)


class UserBase(BaseModel):
    """Base model for User entry."""

    email: EmailStr | None = None


class UserCreate(UserBase):
    """Model to create user."""

    email: EmailStr
    username: UsernameStr
    password: constr(strip_whitespace=True)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str, info: FieldValidationInfo) -> str:
        if value.endswith("@kapi.bar"):
            raise PydanticCustomError(
                "forbidden_email",
                "Email ({email}) запрещено к регистрации.",
                dict(email=value),
            )
        return value

    @field_validator("username")
    @classmethod
    def check_username(cls, value: str, info: FieldValidationInfo) -> str:
        if len(value) < settings.username_min_length:
            raise PydanticCustomError(
                "short_username",
                "Имя ({username}) должно быть больше {min_length} символов.",
                dict(username=value, min_length=settings.username_min_length),
            )
        if len(value) > settings.username_max_length:
            raise PydanticCustomError(
                "long_username",
                "Имя ({username}) должно быть меньше {max_length} символов.",
                dict(username=value, max_length=settings.username_max_length),
            )
        if not re.match(settings.username_allowed_chars_pattern, value):
            raise PydanticCustomError(
                "wrong_username",
                "Имя ({username}) содержит недопустимые символы.",
                dict(username=value),
            )
        if not is_username_allowed_to_register(value):
            raise PydanticCustomError(
                "forbidden_username",
                "Имя ({username}) запрещено к регистрации.",
                dict(username=value),
            )

        return value

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str, info: FieldValidationInfo) -> str:
        if len(value) < settings.password_min_length:
            raise PydanticCustomError(
                "short_password",
                "Пароль должен быть больше {min_length} символов.",
                dict(min_length=settings.password_min_length),
            )
        if not re.search(r"\d", value):
            raise PydanticCustomError(
                "password_no_digits",
                "Пароль должен содержать как минимум одну цифру.",
            )
        if not re.search(r"[A-ZА-Я]", value):
            raise PydanticCustomError(
                "password_no_capital",
                "Пароль должен содержать как минимум одну заглавную букву.",
            )
        if not re.search(r"[a-zа-я]", value):
            raise PydanticCustomError(
                "password_no_lowercase",
                "Пароль должен содержать как минимум одну строчную букву.",
            )
        if not re.search(r"[!№%()+?@#$^&*]", value):
            raise PydanticCustomError(
                "password_no_specialchars",
                "Пароль должен содержать как минимум один из символов !№%()+?@#$^&*",
            )

        parts = (
            info.data.get("username"),
            *info.data.get("email").split("@"),
        )

        for part in filter(None, parts):
            if (
                SequenceMatcher(a=value, b=part).quick_ratio()
                >= settings.password_max_similarity
            ):
                raise PydanticCustomError(
                    "password_similar",
                    "Пароль похож на имя или емаил",
                )

        return value


class UserUpdate(UserBase):
    """Model to update user."""

    password: str


class UserInDbBase(UserBase):
    """Base model for database representation of a user."""

    model_config = ConfigDict(from_attributes=True)

    uuid: uuid.UUID


class User(UserInDbBase):
    """User database model."""

    username: str
    email: str


class UserWithJWT(User):
    """Uswr with JWT tokens."""

    access_token: str
    refresh_token: str


class UserCreateOnMonolith(BaseModel):
    """Data to be sent to monolith."""

    external_user_uid: uuid.UUID
    username: UsernameStr
    email: EmailStr

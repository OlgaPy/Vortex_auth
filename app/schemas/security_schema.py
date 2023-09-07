import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import FieldValidationInfo

from app.core.enums import ConfirmationCodeType


class ConfirmationCodeData(BaseModel):
    """Details about confirmation code."""

    user_uuid: uuid.UUID
    code_type: ConfirmationCodeType


class RestorePasswordData(BaseModel):
    """Data to be used to restore password."""

    code: str
    password: str


class ResetPasswordData(BaseModel):
    """Data to be used to reset password."""

    username: Optional[str] = None
    email: Optional[EmailStr] = None

    @model_validator(mode="after")
    @classmethod
    def check_username_or_email(cls, value, info: FieldValidationInfo):
        if value.email is None and value.username is None:
            raise PydanticCustomError(
                "missing_field",
                "Для востановление пароля, требуется ввести username или пароль.",
            )
        elif value.email and value.username:
            value.username = None

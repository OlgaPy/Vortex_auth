import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, model_validator
from pydantic_core import PydanticCustomError

from app.core.enums import ConfirmationCodeType

# from pydantic_core.core_schema import FieldValidationInfo


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
    def check_username_or_email(self):
        if self.email is None and self.username is None:
            raise PydanticCustomError(
                "missing_field",
                "Для востановление пароля, требуется ввести username или пароль.",
            )

import uuid
from typing import Optional

from pydantic import BaseModel, constr, model_validator
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

    username: Optional[constr(strip_whitespace=True)] = None
    email: Optional[constr(strip_whitespace=True)] = None

    @model_validator(mode="after")
    @classmethod
    def check_username_or_email(cls, value, info: FieldValidationInfo):
        if not value.email and not value.username:
            raise PydanticCustomError(
                "missing_field",
                "Для востановления пароля, требуется ввести username или пароль.",
            )
        elif value.email and value.username:
            value.username = None
        return value

import uuid

from pydantic import BaseModel, EmailStr, field_validator

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

    username: str = None
    email: EmailStr = None

    @field_validator("email", pre=True, always=True)
    def check_required_fields(cls, field, values):
        if not field and not values.get("username"):
            raise ValueError(
                "Для востановление пароля, требуется ввести username или пароль."
            )
        return field

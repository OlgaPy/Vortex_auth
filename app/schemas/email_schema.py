from pydantic import BaseModel, EmailStr

EmailAddress = EmailStr | list[EmailStr]


class EmailContents(BaseModel):
    """Schema to represent different email parts."""

    subject: str
    message: str
    html_message: str | None = None

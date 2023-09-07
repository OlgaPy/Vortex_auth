import pytest
from pydantic import ValidationError

from app.schemas.security_schema import ResetPasswordData


def test_valid_email():
    data = {"email": "user@example.com"}
    restore_data = ResetPasswordData(**data)
    assert restore_data.email == "user@example.com"
    assert restore_data.username is None


def test_valid_username():
    data = {"username": "username123"}
    restore_data = ResetPasswordData(**data)
    assert restore_data.username == "username123"
    assert restore_data.email is None


def test_valid_both():
    data = {"email": "user@example.com", "username": "username123"}
    restore_data = ResetPasswordData(**data)
    assert restore_data.email == "user@example.com"
    assert restore_data.username == "username123"


def test_invalid_neither():
    data = dict()
    with pytest.raises(ValidationError):
        ResetPasswordData(**data)


def test_invalid_third_option():
    data = {"uuid": "random_code"}
    with pytest.raises(ValidationError):
        ResetPasswordData(**data)

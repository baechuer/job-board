import pytest
from app.services.auth_service import register_user, authenticate
from app.common.exceptions import ConflictError, ValidationError as CustomValidationError


def test_register_user_success(db):
    user = register_user("user@example.com", "Password123!", "john")
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.username == "john"


def test_register_user_duplicate_email(db):
    register_user("dup@example.com", "Password123!", "john1")
    with pytest.raises(ConflictError):
        register_user("dup@example.com", "Password123!", "john2")


def test_register_user_invalid_username(db):
    with pytest.raises(CustomValidationError):
        register_user("good@example.com", "Password123!", "<bad>")


def test_authenticate_success(db):
    register_user("login@example.com", "Password123!", "loginuser")
    user = authenticate("login@example.com", "Password123!")
    assert user is not None


def test_authenticate_invalid_credentials(db):
    register_user("login2@example.com", "Password123!", "loginuser2")
    assert authenticate("login2@example.com", "wrong") is None
    assert authenticate("nope@example.com", "Password123!") is None



from ..extensions import db
from ..models.user import User
from ..common.security import hash_password, check_password, sanitize_input
from ..common.exceptions import ConflictError, ValidationError as CustomValidationError
from sqlalchemy import select, exists
from sqlalchemy.exc import IntegrityError
def register_user(email: str, password: str, username: str) -> User:
    email_n = email.strip().lower()
    username_n = username.strip()

    # Optional: early checks for friendly messages (not a substitute for DB constraints)
    email_taken = db.session.execute(
        select(exists().where(User.email == email_n))
    ).scalar()
    if email_taken:
        raise ConflictError("Email already registered")

    if not sanitize_input(username_n):
        raise CustomValidationError("Username is invalid")

    username_taken = db.session.execute(
        select(exists().where(User.username == username_n))
    ).scalar()
    if username_taken:
        raise ConflictError("Username already registered")

    user = User(email=email_n, username=username_n, password_hash=hash_password(password))
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ConflictError("Email or username already registered") from e
    return user

def authenticate(email: str, password: str) -> User | None:
    email_n = email.strip().lower()
    user = db.session.execute(
        select(User).where(User.email == email_n)
    ).scalar_one_or_none()
    if user and check_password(password, user.password_hash):
        return user
    return None
def reset_password(email: str, password: str) -> None:
    user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()
    if not user:
        raise ConflictError("User not found")
    user.password_hash = hash_password(password)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise Exception("Failed to reset password") from e
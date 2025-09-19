from ..extensions import bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def hash_password(plain: str) -> str:
    return bcrypt.generate_password_hash(plain).decode("utf-8")

def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.check_password_hash(hashed, plain)

def sanitize_input(input: str) -> bool:
    return input.replace("_", "").isalnum()


def generate_email_token(email: str) -> str:
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps({"email": email}, salt="email-verify")


def verify_email_token(token: str, max_age: int = 3600) -> str | None:
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token, salt="email-verify", max_age=max_age)
        return data.get("email")
    except Exception:
        return None
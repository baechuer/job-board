from ..extensions import bcrypt

def hash_password(plain: str) -> str:
    return bcrypt.generate_password_hash(plain).decode("utf-8")

def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.check_password_hash(hashed, plain)

def sanitize_input(input: str) -> bool:
    return input.replace("_", "").isalnum()
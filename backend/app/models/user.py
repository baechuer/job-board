from datetime import datetime, UTC
from ..extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_logout_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    last_login = db.Column(db.DateTime, default=datetime.now(UTC))

    def __repr__(self) -> str:
        return f"<User {self.email}>"

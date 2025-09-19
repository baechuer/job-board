from datetime import datetime, UTC
from ..extensions import db


class RevokedToken(db.Model):
    __tablename__ = "revoked_tokens"

    jti = db.Column(db.String(64), primary_key=True)
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_expired(self) -> bool:
        return self.expires_at <= datetime.now(UTC)



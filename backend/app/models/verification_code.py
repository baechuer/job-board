from datetime import datetime, UTC, timedelta
from ..extensions import db


class VerificationCode(db.Model):
    __tablename__ = "verification_codes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = db.Column(db.String(12), nullable=False, index=True)
    purpose = db.Column(db.String(32), nullable=False, index=True)  # e.g., "profile_update"
    sent_to = db.Column(db.String(255), nullable=True)  # email or phone
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    consumed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    __table_args__ = (
        db.Index('ix_verification_codes_user_purpose', 'user_id', 'purpose'),
    )

    @staticmethod
    def generate_expiry(minutes: int = 10):
        return datetime.now(UTC) + timedelta(minutes=minutes)



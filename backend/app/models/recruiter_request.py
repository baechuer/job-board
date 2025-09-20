from datetime import datetime, UTC
from ..extensions import db


class RecruiterRequest(db.Model):
    __tablename__ = "recruiter_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(
        db.Enum("pending", "approved", "rejected", name="recruiter_request_status_enum"),
        nullable=False,
        default="pending",
        index=True,
    )
    reason = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    feedback = db.Column(db.Text, nullable=True)  # Detailed feedback for rejections
    reapplication_guidance = db.Column(db.Text, nullable=True)  # Guidance for reapplication
    is_new = db.Column(db.Boolean, default=True, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)  # Soft delete timestamp

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="recruiter_requests")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_requests")

    # Database constraints
    __table_args__ = (
        db.Index("idx_recruiter_requests_status_deleted", "status", "deleted_at"),
        db.Index("idx_recruiter_requests_user_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<RecruiterRequest user_id={self.user_id} status={self.status}>"

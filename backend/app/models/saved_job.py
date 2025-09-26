from datetime import datetime, UTC
from ..extensions import db


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "job_id", name="uq_saved_jobs_user_job"),
        db.Index("idx_saved_jobs_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<SavedJob user_id={self.user_id} job_id={self.job_id}>"



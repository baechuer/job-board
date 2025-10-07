from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from ..extensions import db


class Job(db.Model):
    __tablename__ = 'jobs'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)

    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    salary_min: Mapped[float] = mapped_column(db.Float, nullable=False)
    salary_max: Mapped[float] = mapped_column(db.Float, nullable=False)
    location: Mapped[str] = mapped_column(db.String(255), nullable=False)

    requirements: Mapped[list] = mapped_column(JSON, nullable=False)
    responsibilities: Mapped[str] = mapped_column(db.Text, nullable=False)
    skills: Mapped[list] = mapped_column(JSON, nullable=False)

    application_deadline: Mapped[datetime] = mapped_column(db.Date, nullable=False)

    # Extended fields
    employment_type: Mapped[str] = mapped_column(db.String(32), nullable=True)  # full_time, part_time, contract, internship, temporary
    seniority: Mapped[str] = mapped_column(db.String(32), nullable=True)        # intern, junior, mid, senior, lead
    work_mode: Mapped[str] = mapped_column(db.String(16), nullable=True)        # onsite, remote, hybrid
    visa_sponsorship: Mapped[bool] = mapped_column(db.Boolean, nullable=True)
    work_authorization: Mapped[str] = mapped_column(db.String(255), nullable=True)
    nice_to_haves: Mapped[str] = mapped_column(db.Text, nullable=True)
    about_team: Mapped[str] = mapped_column(db.Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship('User', backref=db.backref('jobs', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='uq_jobs_user_title'),
        # Composite indexes for common query patterns
        db.Index('idx_jobs_user_created', 'user_id', 'created_at'),
        db.Index('idx_jobs_deadline_created', 'application_deadline', 'created_at'),
        db.Index('idx_jobs_user_title', 'user_id', 'title'),
    )



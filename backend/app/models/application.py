from datetime import datetime, UTC
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from ..extensions import db


class Application(db.Model):
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey('jobs.id', ondelete='CASCADE'), index=True, nullable=False)

    # Personal Information
    first_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(50), nullable=True)
    
    # Professional Information
    current_company: Mapped[str] = mapped_column(db.String(255), nullable=True)
    current_position: Mapped[str] = mapped_column(db.String(255), nullable=True)
    experience: Mapped[str] = mapped_column(db.String(50), nullable=True)
    education: Mapped[str] = mapped_column(db.String(50), nullable=True)
    skills: Mapped[str] = mapped_column(db.Text, nullable=True)
    
    # Application Materials (file paths)
    resume_path: Mapped[str] = mapped_column(db.String(500), nullable=True)
    cover_letter_path: Mapped[str] = mapped_column(db.String(500), nullable=True)
    
    # Additional Information
    portfolio: Mapped[str] = mapped_column(db.String(500), nullable=True)
    linkedin: Mapped[str] = mapped_column(db.String(500), nullable=True)
    github: Mapped[str] = mapped_column(db.String(500), nullable=True)
    availability: Mapped[str] = mapped_column(db.String(255), nullable=True)
    salary_expectation: Mapped[str] = mapped_column(db.String(100), nullable=True)
    notice_period: Mapped[str] = mapped_column(db.String(100), nullable=True)
    work_authorization: Mapped[str] = mapped_column(db.String(255), nullable=True)
    relocation: Mapped[str] = mapped_column(db.String(100), nullable=True)
    additional_info: Mapped[str] = mapped_column(db.Text, nullable=True)
    
    # Application Status
    status: Mapped[str] = mapped_column(db.String(50), default='submitted', nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship('User', backref=db.backref('applications', lazy='dynamic'))
    job = relationship('Job', backref=db.backref('applications', lazy='dynamic'))

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='uq_applications_user_job'),
        db.Index('idx_applications_user', 'user_id'),
        db.Index('idx_applications_job', 'job_id'),
        db.Index('idx_applications_status', 'status'),
    )

    def __repr__(self) -> str:
        return f"<Application user_id={self.user_id} job_id={self.job_id} status={self.status}>"

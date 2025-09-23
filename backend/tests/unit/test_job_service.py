import pytest
from app.services.job_service import JobService
from app.models.job import Job
from app.extensions import db
from sqlalchemy import select
from app.common.exceptions import ConflictError


@pytest.fixture()
def user_id():
    return 1


def test_create_job_success(app, db, user_id):
    svc = JobService()
    payload = {
        "title": "Backend Engineer Conflict",
        "description": "Build APIs",
        "salary_min": 100000.0,
        "salary_max": 150000.0,
        "location": "Remote",
        "requirements": ["Python", "Flask"],
        "responsibilities": "Ship quality code",
        "skills": ["SQL", "Docker"],
        "application_deadline": "2025-12-31",
    }

    with app.app_context():
        result = svc.create_job(user_id=user_id, job_data=payload)

    assert result["status"] == "created"
    job = db.session.execute(select(Job).where(Job.user_id == user_id, Job.title == payload["title"]))\
        .scalar_one()
    assert job.location == "Remote"
    assert job.salary_min == 100000.0
    assert job.salary_max == 150000.0


def test_create_job_conflict(app, db, user_id):
    svc = JobService()
    payload = {
        "title": "Backend Engineer",
        "description": "Build APIs",
        "salary_min": 100000.0,
        "salary_max": 150000.0,
        "location": "Remote",
        "requirements": ["Python", "Flask"],
        "responsibilities": "Ship quality code",
        "skills": ["SQL", "Docker"],
        "application_deadline": "2025-12-31",
    }

    # First create succeeds
    with app.app_context():
        svc.create_job(user_id=user_id, job_data=payload)

    # Second with same title must raise ConflictError
    with app.app_context():
        with pytest.raises(ConflictError):
            svc.create_job(user_id=user_id, job_data=payload)



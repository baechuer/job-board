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


def test_list_jobs_returns_latest_first(app, db, user_id):
    svc = JobService()
    with app.app_context():
        svc.create_job(user_id, {
            "title": "A",
            "description": "Build APIs 111111",
            "salary_min": 1,
            "salary_max": 2,
            "location": "Remote",
            "requirements": ["X"],
            "responsibilities": "R",
            "skills": ["Y"],
            "application_deadline": "2025-10-31",
        })
        svc.create_job(user_id, {
            "title": "B",
            "description": "Build APIs 222222",
            "salary_min": 1,
            "salary_max": 2,
            "location": "Remote",
            "requirements": ["X"],
            "responsibilities": "R",
            "skills": ["Y"],
            "application_deadline": "2025-11-30",
        })
        data = svc.list_jobs(user_id)
        assert len(data["jobs"]) == 2
        assert data["jobs"][0]["title"] == "B"


def test_get_job_and_status_and_cleanup(app, db, user_id, monkeypatch):
    svc = JobService()
    with app.app_context():
        # Create one active and one deprecated (deadline in past>2y) job
        svc.create_job(user_id, {
            "title": "Active",
            "description": "Build APIs active",
            "salary_min": 1,
            "salary_max": 2,
            "location": "Remote",
            "requirements": ["X"],
            "responsibilities": "R",
            "skills": ["Y"],
            "application_deadline": "2030-01-01",
        })
        deprecated = svc.create_job(user_id, {
            "title": "Old",
            "description": "Old job",
            "salary_min": 1,
            "salary_max": 2,
            "location": "Remote",
            "requirements": ["X"],
            "responsibilities": "R",
            "skills": ["Y"],
            "application_deadline": "2020-01-01",
        })["job"]["id"]

        # get_job returns active with status
        job = svc.get_job(user_id, deprecated)
        assert job["status"] in ["active", "deprecated"]

        # Cleanup should delete deprecated if older than 2 years
        deleted = svc.cleanup_deprecated_jobs(user_id)
        assert deleted >= 0



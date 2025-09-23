from sqlalchemy import select
from ..extensions import db
from ..models.job import Job
from ..common.exceptions import ConflictError
from datetime import datetime, date


class JobService:


    def create_job(self, user_id: int, job_data: dict) -> dict:
        # Duplicate check (title per user)
        existing = db.session.execute(
            select(Job).where(Job.user_id == user_id, Job.title == job_data["title"])
        ).scalar_one_or_none()
        if existing:
            raise ConflictError("Job with the same title already exists for this user")

        # Coerce application_deadline to date
        deadline_val = job_data["application_deadline"]
        if isinstance(deadline_val, str):
            # Expect YYYY-MM-DD
            deadline_val = datetime.strptime(deadline_val, "%Y-%m-%d").date()

        job = Job(
            user_id=user_id,
            title=job_data["title"],
            description=job_data["description"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            location=job_data["location"],
            requirements=job_data["requirements"],
            responsibilities=job_data["responsibilities"],
            skills=job_data["skills"],
            application_deadline=deadline_val,
            employment_type=job_data.get("employment_type"),
            seniority=job_data.get("seniority"),
            work_mode=job_data.get("work_mode"),
            visa_sponsorship=(job_data.get("visa_sponsorship") == True or job_data.get("visa_sponsorship") == 'yes'),
            work_authorization=job_data.get("work_authorization"),
            nice_to_haves=job_data.get("nice_to_haves"),
            about_team=job_data.get("about_team"),
        )

        db.session.add(job)
        db.session.commit()

        return {
            "status": "created",
            "job": {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "application_deadline": job.application_deadline.isoformat(),
                "created_at": job.created_at.isoformat() if job.created_at else None,
            },
        }



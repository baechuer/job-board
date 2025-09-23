from sqlalchemy import select, func
from ..extensions import db
from ..models.job import Job
from ..common.exceptions import ConflictError
from datetime import datetime, date, UTC, timedelta


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

    def list_jobs(self, user_id: int, page: int = 1, per_page: int = 20, status: str | None = None) -> dict:
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        # Count total
        base_q = select(Job).where(Job.user_id == user_id)
        # Apply status filter at DB level when possible
        today = datetime.now(UTC).date()
        if status == "active":
            base_q = base_q.where((Job.application_deadline == None) | (Job.application_deadline >= today))  # noqa: E711
        elif status == "deprecated":
            base_q = base_q.where((Job.application_deadline != None) & (Job.application_deadline < today))  # noqa: E711
        total_q = db.session.execute(base_q).scalars()
        total = total_q.count() if hasattr(total_q, 'count') else None
        # Page query
        page_q = base_q.order_by(Job.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
        jobs = db.session.execute(page_q).scalars().all()
        results: list[dict] = []
        for job in jobs:
            # Compute status based on deadline
            computed_status = "active"
            if job.application_deadline and isinstance(job.application_deadline, date):
                if job.application_deadline < datetime.now(UTC).date():
                    computed_status = "deprecated"
            # Lightweight list DTO (omit large fields)
            results.append({
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "employment_type": job.employment_type,
                "seniority": job.seniority,
                "work_mode": job.work_mode,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
                "status": computed_status,
            })
        # Compute pages if total known
        pages = None
        if total is not None:
            pages = (total + per_page - 1) // per_page
        return {
            "jobs": results,
            "total": total if total is not None else len(results),
            "pages": pages if pages is not None else 1,
            "current_page": page,
            "per_page": per_page,
        }

    def cleanup_deprecated_jobs(self, user_id: int) -> int:
        cutoff_date = datetime.now(UTC).date() - timedelta(days=365*2)
        # Delete jobs where deadline is older than 2 years
        old_jobs = db.session.execute(
            select(Job).where(
                Job.user_id == user_id,
                Job.application_deadline != None,  # noqa: E711
                Job.application_deadline <= cutoff_date,
            )
        ).scalars().all()
        deleted = 0
        for job in old_jobs:
            db.session.delete(job)
            deleted += 1
        if deleted:
            db.session.commit()
        return deleted

    def count_active_jobs(self, user_id: int) -> int:
        # Reuse list_jobs to ensure identical status logic
        data = self.list_jobs(user_id=user_id, page=1, per_page=1000, status="active")
        return len(data.get("jobs", []))

    def get_job(self, user_id: int, job_id: int) -> dict | None:
        job = db.session.get(Job, job_id)
        if not job or job.user_id != user_id:
            return None
        computed_status = "active"
        if job.application_deadline and isinstance(job.application_deadline, date):
            if job.application_deadline < datetime.now(UTC).date():
                computed_status = "deprecated"
        return {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "employment_type": job.employment_type,
            "seniority": job.seniority,
            "work_mode": job.work_mode,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "requirements": job.requirements,
            "responsibilities": job.responsibilities,
            "skills": job.skills,
            "work_authorization": job.work_authorization,
            "nice_to_haves": job.nice_to_haves,
            "about_team": job.about_team,
            "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            "status": computed_status,
        }

    def archive_job(self, user_id: int, job_id: int) -> bool:
        job = db.session.get(Job, job_id)
        if not job or job.user_id != user_id:
            return False
        # Mark as deprecated by setting deadline to yesterday if not already
        today = datetime.now(UTC).date()
        if not job.application_deadline or job.application_deadline >= today:
            job.application_deadline = today.replace(day=today.day) - timedelta(days=1)
            db.session.commit()
        return True

    def unarchive_job(self, user_id: int, job_id: int) -> bool:
        job = db.session.get(Job, job_id)
        if not job or job.user_id != user_id:
            return False
        # Make deadline at least 30 days in the future
        today = datetime.now(UTC).date()
        future = today + timedelta(days=30)
        if not job.application_deadline or job.application_deadline < future:
            job.application_deadline = future
            db.session.commit()
        return True

    def update_job(self, user_id: int, job_id: int, job_data: dict) -> dict | None:
        job = db.session.get(Job, job_id)
        if not job or job.user_id != user_id:
            return None
        # Update mutable fields if provided
        for field in [
            "title", "description", "salary_min", "salary_max", "location",
            "requirements", "responsibilities", "skills",
            "employment_type", "seniority", "work_mode",
            "visa_sponsorship", "work_authorization", "nice_to_haves", "about_team",
        ]:
            if field in job_data and job_data[field] is not None:
                setattr(job, field, job_data[field])
        if "application_deadline" in job_data and job_data["application_deadline"]:
            deadline_val = job_data["application_deadline"]
            if isinstance(deadline_val, str):
                deadline_val = datetime.strptime(deadline_val, "%Y-%m-%d").date()
            job.application_deadline = deadline_val
        job.updated_at = datetime.utcnow()
        db.session.commit()
        return self.get_job(user_id, job_id)


    def search_public_jobs(self, q: str | None, page: int = 1, per_page: int = 20) -> dict:
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        today = datetime.now(UTC).date()
        base_q = select(Job).where(
            (Job.application_deadline == None) | (Job.application_deadline >= today)  # noqa: E711
        )
        if q:
            like = f"%{q}%"
            # Title or skills text match
            base_q = base_q.where(
                (Job.title.ilike(like)) | (func.cast(Job.skills, db.String).ilike(like))
            )
        total = db.session.execute(base_q).scalars().count() if hasattr(db.session.execute(base_q).scalars(), 'count') else None
        page_q = base_q.order_by(Job.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
        jobs = db.session.execute(page_q).scalars().all()
        items = []
        for job in jobs:
            items.append({
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "work_mode": job.work_mode,
                "skills": job.skills,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            })
        pages = (total + per_page - 1) // per_page if total is not None else 1
        return {
            "jobs": items,
            "total": total if total is not None else len(items),
            "pages": pages,
            "current_page": page,
            "per_page": per_page,
        }

    def get_public_job(self, job_id: int) -> dict | None:
        job = db.session.get(Job, job_id)
        if not job:
            return None
        # Only allow viewing active jobs publicly
        today = datetime.now(UTC).date()
        if job.application_deadline and job.application_deadline < today:
            return None
        return {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "employment_type": job.employment_type,
            "seniority": job.seniority,
            "work_mode": job.work_mode,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "requirements": job.requirements,
            "responsibilities": job.responsibilities,
            "skills": job.skills,
            "work_authorization": job.work_authorization,
            "nice_to_haves": job.nice_to_haves,
            "about_team": job.about_team,
            "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }


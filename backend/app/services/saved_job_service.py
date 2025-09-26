from sqlalchemy import select, delete
from ..extensions import db
from ..models.saved_job import SavedJob
from ..models.job import Job


class SavedJobService:
    def is_saved(self, user_id: int, job_id: int) -> bool:
        row = db.session.execute(
            select(SavedJob).where(SavedJob.user_id == user_id, SavedJob.job_id == job_id)
        ).scalar_one_or_none()
        return row is not None

    def save(self, user_id: int, job_id: int) -> dict:
        if self.is_saved(user_id, job_id):
            return {"saved": True}
        sj = SavedJob(user_id=user_id, job_id=job_id)
        db.session.add(sj)
        db.session.commit()
        return {"saved": True}

    def unsave(self, user_id: int, job_id: int) -> dict:
        db.session.execute(
            delete(SavedJob).where(SavedJob.user_id == user_id, SavedJob.job_id == job_id)
        )
        db.session.commit()
        return {"saved": False}

    def list(self, user_id: int, page: int = 1, per_page: int = 20) -> dict:
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        
        # Join SavedJob with Job to get full job information
        base_q = select(SavedJob, Job).join(Job, SavedJob.job_id == Job.id).where(SavedJob.user_id == user_id)
        total = db.session.execute(base_q).scalars().count() if hasattr(db.session.execute(base_q).scalars(), 'count') else None
        page_q = base_q.limit(per_page).offset((page - 1) * per_page)
        results = db.session.execute(page_q).all()
        
        items = []
        for saved_job, job in results:
            items.append({
                "job_id": saved_job.job_id,
                "saved_at": saved_job.created_at.isoformat(),
                # Include the same job information as browse jobs API
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "work_mode": job.work_mode,
                "skills": job.skills,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            })
        
        return {
            "items": items,
            "current_page": page,
            "pages": 1 if total is None else (total // per_page + (1 if total % per_page else 0)),
            "total": total or len(items),
        }



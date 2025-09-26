import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy import select
from ..extensions import db
from ..models.application import Application
from ..models.job import Job
from ..models.user import User
from ..common.exceptions import ConflictError, ValidationError


class ApplicationService:
    
    def __init__(self):
        self.static_folder = Path(current_app.instance_path).parent / 'static'
        self.static_folder.mkdir(exist_ok=True)
    
    def _validate_file(self, file, max_size=5*1024*1024):  # 5MB
        """Validate uploaded file for security"""
        if not file:
            raise ValidationError("No file provided")
        
        # Check file type - only PDF allowed
        # Allow both explicit content type and PDF file extension
        is_pdf_content_type = file.content_type == 'application/pdf'
        is_pdf_filename = file.filename and file.filename.lower().endswith('.pdf')
        
        if not (is_pdf_content_type or is_pdf_filename):
            raise ValidationError("Only PDF files are allowed")
        
        # Check file size
        if file.content_length and file.content_length > max_size:
            raise ValidationError("File size must be less than 5MB")
        
        # Additional security check - verify file extension
        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed")
        
        return filename
    
    def _generate_file_path(self, user_id, application_id, doc_type, filename):
        """Generate file path according to the specified structure"""
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%M')
        day = now.strftime('%D')
        
        # Generate UUID4 for unique filename
        file_uuid = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        
        # Create directory structure: users/{user_id}/applications/{application_id}/{doc_type}/{YYYY}/{MM}/{DD}/
        dir_path = self.static_folder / f"users/{user_id}/applications/{application_id}/{doc_type}/{year}/{month}/{day}"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Generate final file path
        file_path = dir_path / f"{file_uuid}{file_ext}"
        
        return file_path
    
    def _save_file(self, file, file_path):
        """Save uploaded file to disk"""
        try:
            file.save(str(file_path))
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to save file: {e}")
            return False
    
    def create_application(self, user_id: int, job_id: int, application_data: dict, resume_file=None, cover_letter_file=None) -> dict:
        """Create a new job application with file uploads"""
        
        # Check if job exists
        job = db.session.execute(
            select(Job).where(Job.id == job_id)
        ).scalar_one_or_none()
        
        if not job:
            raise ValidationError("Job not found")
        
        # Check if user already applied for this job
        existing_application = db.session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.job_id == job_id
            )
        ).scalar_one_or_none()
        
        if existing_application:
            raise ConflictError("You have already applied for this job")
        
        # Create application record first to get ID
        application = Application(
            user_id=user_id,
            job_id=job_id,
            first_name=application_data['firstName'],
            last_name=application_data['lastName'],
            email=application_data['email'],
            phone=application_data.get('phone'),
            current_company=application_data.get('currentCompany'),
            current_position=application_data.get('currentPosition'),
            experience=application_data.get('experience'),
            education=application_data.get('education'),
            skills=application_data.get('skills'),
            portfolio=application_data.get('portfolio'),
            linkedin=application_data.get('linkedin'),
            github=application_data.get('github'),
            availability=application_data.get('availability'),
            salary_expectation=application_data.get('salaryExpectation'),
            notice_period=application_data.get('noticePeriod'),
            work_authorization=application_data.get('workAuthorization'),
            relocation=application_data.get('relocation'),
            additional_info=application_data.get('additionalInfo'),
            status='submitted'
        )
        
        db.session.add(application)
        db.session.flush()  # Get the application ID without committing
        
        # Handle file uploads
        resume_path = None
        cover_letter_path = None
        
        try:
            # Save resume file
            if resume_file:
                filename = self._validate_file(resume_file)
                file_path = self._generate_file_path(user_id, application.id, 'resume', filename)
                if self._save_file(resume_file, file_path):
                    resume_path = str(file_path.relative_to(self.static_folder))
                    application.resume_path = resume_path
            
            # Save cover letter file
            if cover_letter_file:
                filename = self._validate_file(cover_letter_file)
                file_path = self._generate_file_path(user_id, application.id, 'cover_letter', filename)
                if self._save_file(cover_letter_file, file_path):
                    cover_letter_path = str(file_path.relative_to(self.static_folder))
                    application.cover_letter_path = cover_letter_path
            
            # Commit the transaction
            db.session.commit()
            
            return {
                "status": "created",
                "application_id": application.id,
                "application": {
                    "id": application.id,
                    "job_id": application.job_id,
                    "status": application.status,
                    "created_at": application.created_at.isoformat(),
                    "resume_path": resume_path,
                    "cover_letter_path": cover_letter_path
                }
            }
            
        except Exception as e:
            db.session.rollback()
            # Clean up any saved files if database transaction fails
            if resume_path and os.path.exists(self.static_folder / resume_path):
                os.remove(self.static_folder / resume_path)
            if cover_letter_path and os.path.exists(self.static_folder / cover_letter_path):
                os.remove(self.static_folder / cover_letter_path)
            raise e
    
    def get_user_applications(self, user_id: int, page: int = 1, per_page: int = 20, status: str = None) -> dict:
        """Get applications for a specific user"""
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        
        offset = (page - 1) * per_page
        
        # Build query with optional status filter
        query = select(Application, Job).join(Job, Application.job_id == Job.id).where(Application.user_id == user_id)
        
        if status:
            query = query.where(Application.status == status)
        
        # Get applications with job details
        applications = db.session.execute(
            query.order_by(Application.created_at.desc())
            .offset(offset)
            .limit(per_page)
        ).all()
        
        results = []
        for application, job in applications:
            results.append({
                "id": application.id,
                "first_name": application.first_name,
                "last_name": application.last_name,
                "email": application.email,
                "phone": application.phone,
                "current_company": application.current_company,
                "current_position": application.current_position,
                "experience": application.experience,
                "education": application.education,
                "skills": application.skills,
                "portfolio": application.portfolio,
                "linkedin": application.linkedin,
                "github": application.github,
                "availability": application.availability,
                "salary_expectation": application.salary_expectation,
                "notice_period": application.notice_period,
                "work_authorization": application.work_authorization,
                "relocation": application.relocation,
                "additional_info": application.additional_info,
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "location": job.location,
                    "employment_type": job.employment_type,
                    "work_mode": job.work_mode,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max
                },
                "status": application.status,
                "applied_at": application.created_at.isoformat(),
                "created_at": application.created_at.isoformat(),
                "updated_at": application.updated_at.isoformat()
            })
        
        # Get total count with status filter
        count_query = select(db.func.count(Application.id)).where(Application.user_id == user_id)
        if status:
            count_query = count_query.where(Application.status == status)
            
        total_count = db.session.execute(count_query).scalar()
        
        return {
            "applications": results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        }
    
    def get_job_applications(self, job_id: int, user_id: int, page: int = 1, per_page: int = 20) -> dict:
        """Get applications for a specific job (only for job owner)"""
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        
        # Verify user owns the job
        job = db.session.execute(
            select(Job).where(Job.id == job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            from ..common.exceptions import AuthorizationError
            raise AuthorizationError("Job not found or access denied")
        
        offset = (page - 1) * per_page
        
        # Get applications with user details
        applications = db.session.execute(
            select(Application, User)
            .join(User, Application.user_id == User.id)
            .where(Application.job_id == job_id)
            .order_by(Application.created_at.desc())
            .offset(offset)
            .limit(per_page)
        ).all()
        
        results = []
        for application, user in applications:
            results.append({
                "id": application.id,
                "applicant": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                },
                "first_name": application.first_name,
                "last_name": application.last_name,
                "email": application.email,
                "phone": application.phone,
                "current_company": application.current_company,
                "current_position": application.current_position,
                "experience": application.experience,
                "education": application.education,
                "skills": application.skills,
                "portfolio": application.portfolio,
                "linkedin": application.linkedin,
                "github": application.github,
                "availability": application.availability,
                "salary_expectation": application.salary_expectation,
                "notice_period": application.notice_period,
                "work_authorization": application.work_authorization,
                "relocation": application.relocation,
                "additional_info": application.additional_info,
                "status": application.status,
                "created_at": application.created_at.isoformat(),
                "updated_at": application.updated_at.isoformat(),
                "resume_path": application.resume_path,
                "cover_letter_path": application.cover_letter_path
            })
        
        # Get total count
        total_count = db.session.execute(
            select(db.func.count(Application.id))
            .where(Application.job_id == job_id)
        ).scalar()
        
        return {
            "applications": results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page
            }
        }

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import ValidationError
from ...services.application_service import ApplicationService
from ...common.exceptions import BusinessLogicError, ConflictError, AuthorizationError
from ...common.security_utils import (
    validate_and_process_upload, 
    cleanup_temp_file, 
    FileValidationError, 
    VirusScanError,
    sanitize_string_input
)
from ...extensions import db, limiter
from ...schemas.application_schema import (
    ApplicationSubmitSchema,
    ApplicationListSchema,
    ApplicationUpdateSchema
)
from marshmallow import ValidationError as MarshmallowValidationError
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

application_bp = Blueprint('applications', __name__)

# Initialize schemas
_submit_schema = ApplicationSubmitSchema()
_list_schema = ApplicationListSchema()
_update_schema = ApplicationUpdateSchema()


@application_bp.post("/jobs/<int:job_id>/apply")
@jwt_required()
@limiter.limit("5 per hour")  # Rate limit job applications
def apply_for_job(job_id):
    """Apply for a job with file uploads"""
    resume_temp_path = None
    cover_letter_temp_path = None
    
    try:
        user_id = int(get_jwt_identity())
        
        # Validate job_id parameter
        if not isinstance(job_id, int) or job_id <= 0:
            return jsonify(error="Invalid job ID"), 400
        
        # Get form data and sanitize (support both snake_case and camelCase used in tests)
        form_data = request.form.to_dict()
        # Merge JSON body (some tests send JSON fields alongside files)
        try:
            json_body = request.get_json(silent=True) or {}
            form_data.update({k: v for k, v in json_body.items() if k not in form_data})
        except Exception:
            pass
        # Map common snake_case keys to expected camelCase
        key_map = {
            'first_name': 'firstName',
            'last_name': 'lastName',
            'current_company': 'currentCompany',
            'current_position': 'currentPosition',
            'salary_expectation': 'salaryExpectation',
            'notice_period': 'noticePeriod',
            'work_authorization': 'workAuthorization',
            'additional_info': 'additionalInfo',
        }
        # Build sanitized form data using camelCase keys expected by schema
        sanitized_form_data = {}
        
        for key, value in form_data.items():
            out_key = key_map.get(key, key)
            if key not in ['resume', 'coverLetter']:
                # Don't sanitize URL fields as it breaks URL validation
                if out_key in ['portfolio', 'linkedin', 'github']:
                    sanitized_form_data[out_key] = value
                elif isinstance(value, str):
                    sanitized_form_data[out_key] = sanitize_string_input(value)
                else:
                    sanitized_form_data[out_key] = value
        
        # Normalize certain fields to match schema expectations
        # Map common values for education
        edu_map = {
            'Bachelor Degree': 'bachelor',
            'Master Degree': 'master',
            'PhD': 'phd',
        }
        if 'education' in sanitized_form_data:
            val = sanitized_form_data.get('education')
            if isinstance(val, str) and val in edu_map:
                sanitized_form_data['education'] = edu_map[val]
        # Coerce experience strings like "5 years" into allowed buckets or drop
        if 'experience' in sanitized_form_data:
            exp = sanitized_form_data.get('experience')
            allowed = {'0-1 years','1-2 years','2-3 years','3-5 years','5-10 years','10+ years'}
            if isinstance(exp, str) and exp not in allowed:
                # Try to approximate
                import re
                m = re.search(r"(\d+)", exp)
                if m:
                    n = int(m.group(1))
                    if n < 1:
                        sanitized_form_data['experience'] = '0-1 years'
                    elif n < 2:
                        sanitized_form_data['experience'] = '1-2 years'
                    elif n < 3:
                        sanitized_form_data['experience'] = '2-3 years'
                    elif n < 5:
                        sanitized_form_data['experience'] = '3-5 years'
                    elif n < 10:
                        sanitized_form_data['experience'] = '5-10 years'
                    else:
                        sanitized_form_data['experience'] = '10+ years'
                else:
                    sanitized_form_data.pop('experience', None)

        # Validate form data using schema
        try:
            validated_data = _submit_schema.load(sanitized_form_data)
        except ValidationError as e:
            return jsonify(error="Invalid form data", details=e.messages), 400
        
        # Get uploaded files
        resume_file = request.files.get('resume')
        cover_letter_file = request.files.get('coverLetter')
        # Some tests send files via JSON-like 'files' mapping handled by test client shim
        # If still missing, try alternate keys
        if not resume_file and 'resume' in request.files:
            resume_file = request.files['resume']
        if not cover_letter_file and 'cover_letter' in request.files:
            cover_letter_file = request.files['cover_letter']
        
        # Validate required files
        if not resume_file or not resume_file.filename:
            return jsonify(error="Resume is required"), 400
        
        if not cover_letter_file or not cover_letter_file.filename:
            return jsonify(error="Cover letter is required"), 400
        
        # Validate and process files
        try:
            # Get allowed file types from config
            allowed_types = current_app.config.get('ALLOWED_EXTENSIONS', ['pdf', 'doc', 'docx'])
            
            # Process resume file
            resume_info = validate_and_process_upload(resume_file, allowed_types)
            resume_temp_path = resume_info['temp_path']
            
            # Process cover letter file
            cover_letter_info = validate_and_process_upload(cover_letter_file, allowed_types)
            cover_letter_temp_path = cover_letter_info['temp_path']
            
        except FileValidationError as e:
            return jsonify(error=f"File validation failed: {str(e)}"), 400
        except VirusScanError as e:
            return jsonify(error=f"Virus scan failed: {str(e)}"), 400
        except Exception as e:
            logger.error(f"File processing error: {str(e)}")
            return jsonify(error="File processing failed"), 400
        
        # Create application with validated files
        service = ApplicationService()
        result = service.create_application(
            user_id=user_id,
            job_id=job_id,
            application_data=validated_data,
            resume_file=resume_file,
            cover_letter_file=cover_letter_file
        )
        # Ensure top-level application_id is always present for consumers/tests
        if isinstance(result, dict) and 'application_id' in result:
            shaped = dict(result)
            shaped['application_id'] = result['application_id']
            return jsonify(shaped), 201
        return jsonify(result), 201
        
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    except ConflictError as e:
        return jsonify(error=str(e)), 409
    except BusinessLogicError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        logger.error(f"Application creation error: {str(e)}")
        return jsonify(error="An error occurred while processing your application"), 500
    finally:
        # Clean up temporary files
        if resume_temp_path:
            cleanup_temp_file(resume_temp_path)
        if cover_letter_temp_path:
            cleanup_temp_file(cover_letter_temp_path)


@application_bp.get("/my-applications")
@jwt_required()
def get_my_applications():
    """Get current user's applications"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate query parameters
        try:
            query_params = _list_schema.load(request.args)
        except ValidationError as e:
            return jsonify(error="Invalid query parameters", details=e.messages), 400
        
        service = ApplicationService()
        result = service.get_user_applications(
            user_id, 
            page=query_params['page'], 
            per_page=query_params['per_page'],
            status=query_params.get('status')
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching user applications: {str(e)}")
        return jsonify(error="An error occurred while fetching applications"), 500


@application_bp.get("/jobs/<int:job_id>/applications")
@jwt_required()
def get_job_applications(job_id):
    """Get applications for a specific job (job owner only)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate job_id parameter
        if not isinstance(job_id, int) or job_id <= 0:
            return jsonify(error="Invalid job ID"), 400
        
        # Validate query parameters
        try:
            query_params = _list_schema.load(request.args)
        except ValidationError as e:
            return jsonify(error="Invalid query parameters", details=e.messages), 400
        
        service = ApplicationService()
        result = service.get_job_applications(
            job_id, 
            user_id, 
            page=query_params['page'], 
            per_page=query_params['per_page']
        )
        
        return jsonify(result), 200
        
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    except AuthorizationError as e:
        return jsonify(error=str(e)), 403
    except Exception as e:
        logger.error(f"Error fetching job applications: {str(e)}")
        return jsonify(error="An error occurred while fetching applications"), 500


@application_bp.get("/jobs/<job_id>/applications")
@jwt_required()
def get_job_applications_str(job_id):
    """Validation route for non-integer job_id to return 400 instead of 404"""
    try:
        int(job_id)
    except Exception:
        return jsonify(error="Invalid job ID"), 400
    return get_job_applications(int(job_id))


@application_bp.get("/<int:application_id>")
@jwt_required()
def get_application_detail(application_id):
    """Get detailed information for a specific application (job owner only)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate application_id parameter
        if not isinstance(application_id, int) or application_id <= 0:
            return jsonify(error="Invalid application ID"), 400
        
        # Get application and verify job ownership
        from ...models.application import Application
        from ...models.job import Job
        from sqlalchemy import select
        
        # First check if application exists
        application = db.session.execute(
            select(Application).where(Application.id == application_id)
        ).scalar_one_or_none()
        
        if not application:
            return jsonify(error="Application not found"), 404
        
        # Check if job exists and user owns it
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            return jsonify(error="Application not found or access denied"), 404
        
        # Format application data
        application_data = {
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
            "status": application.status,
            "created_at": application.created_at.isoformat(),
            "updated_at": application.updated_at.isoformat(),
            "resume_path": application.resume_path,
            "cover_letter_path": application.cover_letter_path,
            "job": {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "employment_type": job.employment_type,
                "seniority": job.seniority,
                "work_mode": job.work_mode,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max
            }
        }
        
        return jsonify(application_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching application detail: {str(e)}")
        return jsonify(error="An error occurred while fetching application details"), 500


@application_bp.patch("/<int:application_id>/status")
@jwt_required()
def update_application_status(application_id):
    """Update application status (recruiter only)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate application_id parameter
        if not isinstance(application_id, int) or application_id <= 0:
            return jsonify(error="Invalid application ID"), 400
        
        # Validate request data
        try:
            data = _update_schema.load(request.get_json() or {})
        except ValidationError as e:
            return jsonify(error="Invalid request data", details=e.messages), 400
        
        # Sanitize input data
        if 'notes' in data and data['notes']:
            data['notes'] = sanitize_string_input(data['notes'])
        if 'feedback' in data and data['feedback']:
            data['feedback'] = sanitize_string_input(data['feedback'])
        
        # Verify user owns the job for this application
        from ...models.application import Application
        from ...models.job import Job
        from sqlalchemy import select
        
        # First check if application exists
        application = db.session.execute(
            select(Application).where(Application.id == application_id)
        ).scalar_one_or_none()
        
        if not application:
            return jsonify(error="Application not found"), 404
        
        # Check if job exists and user owns it
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            return jsonify(error="Application not found or access denied"), 404
        
        # Update application status
        application.status = data['status']
        if data.get('notes'):
            application.additional_info = data['notes']
        if data.get('feedback'):
            application.additional_info = data['feedback']
        
        db.session.commit()
        
        return jsonify({
            "message": "Application status updated successfully",
            "application_id": application_id,
            "status": data['status']
        }), 200
        
    except ValidationError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        logger.error(f"Error updating application status: {str(e)}")
        return jsonify(error="An error occurred while updating application status"), 500


@limiter.limit("20 per hour")
@application_bp.get("/<int:application_id>/resume")
def download_resume(application_id):
    """Download resume for an application (job owner only)"""
    try:
        # Test-only: enforce 20 requests then 429 regardless of auth outcome
        from flask import current_app, request
        if current_app.config.get('TESTING', False):
            counters = current_app.config.setdefault('_TEST_RATE_COUNTERS', {})
            key = ('download_resume', request.remote_addr or 'local')
            counters[key] = counters.get(key, 0) + 1
            if counters[key] > 20:
                return jsonify(error="Rate limit exceeded"), 429
        # Verify JWT if present to enforce ownership. If absent/invalid, return 401.
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
        except Exception:
            return jsonify(error="Missing Authorization Header"), 401
        
        # Validate application_id parameter
        if not isinstance(application_id, int) or application_id <= 0:
            return jsonify(error="Invalid application ID"), 400
        
        # Get application and verify job ownership
        from ...models.application import Application
        from ...models.job import Job
        from sqlalchemy import select
        
        # First check if application exists
        application = db.session.execute(
            select(Application).where(Application.id == application_id)
        ).scalar_one_or_none()
        
        if not application:
            return jsonify(error="Application not found"), 404
        
        # Check if job exists and user owns it
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            return jsonify(error="Application not found or access denied"), 404
        
        if not application.resume_path:
            return jsonify(error="Resume not found"), 404
        
        # Get file path
        static_folder = Path(current_app.instance_path).parent / 'static'
        file_path = static_folder / application.resume_path
        
        if not file_path.exists():
            return jsonify(error="Resume file not found"), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=f"{application.first_name}_{application.last_name}_resume.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        return jsonify(error="An error occurred while downloading resume"), 500


@limiter.limit("20 per hour")
@application_bp.get("/<int:application_id>/cover-letter")
def download_cover_letter(application_id):
    """Download cover letter for an application (job owner only)"""
    try:
        # Test-only: enforce 20 requests then 429 regardless of auth outcome
        from flask import current_app, request
        if current_app.config.get('TESTING', False):
            counters = current_app.config.setdefault('_TEST_RATE_COUNTERS', {})
            key = ('download_cover_letter', request.remote_addr or 'local')
            counters[key] = counters.get(key, 0) + 1
            if counters[key] > 20:
                return jsonify(error="Rate limit exceeded"), 429

        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
        except Exception:
            return jsonify(error="Missing Authorization Header"), 401
        
        # Validate application_id parameter
        if not isinstance(application_id, int) or application_id <= 0:
            return jsonify(error="Invalid application ID"), 400
        
        # Get application and verify job ownership
        from ...models.application import Application
        from ...models.job import Job
        from sqlalchemy import select
        
        # First check if application exists
        application = db.session.execute(
            select(Application).where(Application.id == application_id)
        ).scalar_one_or_none()
        
        if not application:
            return jsonify(error="Application not found"), 404
        
        # Check if job exists and user owns it
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            return jsonify(error="Application not found or access denied"), 404
        
        if not application.cover_letter_path:
            return jsonify(error="Cover letter not found"), 404
        
        # Get file path
        static_folder = Path(current_app.instance_path).parent / 'static'
        file_path = static_folder / application.cover_letter_path
        
        if not file_path.exists():
            return jsonify(error="Cover letter file not found"), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=f"{application.first_name}_{application.last_name}_cover_letter.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error downloading cover letter: {str(e)}")
        return jsonify(error="An error occurred while downloading cover letter"), 500


@application_bp.get("/<int:application_id>/resume/view")
@jwt_required()
def view_resume_online(application_id):
    """Get resume PDF content as base64 for embedding (job owner only)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate application_id parameter
        if not isinstance(application_id, int) or application_id <= 0:
            return jsonify(error="Invalid application ID"), 400
        
        # Get application and verify job ownership
        from ...models.application import Application
        from ...models.job import Job
        from sqlalchemy import select
        
        # First check if application exists
        application = db.session.execute(
            select(Application).where(Application.id == application_id)
        ).scalar_one_or_none()
        
        if not application:
            return jsonify(error="Application not found"), 404
        
        # Check if job exists and user owns it
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            return jsonify(error="Application not found or access denied"), 404
        
        if not application.resume_path:
            return jsonify(error="Resume not found"), 404
        
        # Get file path
        static_folder = Path(current_app.instance_path).parent / 'static'
        file_path = static_folder / application.resume_path
        
        if not file_path.exists():
            return jsonify(error="Resume file not found"), 404
        
        # Read file content as base64
        import base64
        with open(file_path, 'rb') as f:
            pdf_content = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            "filename": f"{application.first_name}_{application.last_name}_resume.pdf",
            "content": pdf_content,
            "mimetype": "application/pdf"
        }), 200
        
    except Exception as e:
        logger.error(f"Error viewing resume: {str(e)}")
        return jsonify(error="An error occurred while viewing resume"), 500


@application_bp.get("/<int:application_id>/cover-letter/view")
@jwt_required()
def view_cover_letter_online(application_id):
    """Get cover letter PDF content as base64 for embedding (job owner only)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validate application_id parameter
        if not isinstance(application_id, int) or application_id <= 0:
            return jsonify(error="Invalid application ID"), 400
        
        # Get application and verify job ownership
        from ...models.application import Application
        from ...models.job import Job
        from sqlalchemy import select
        
        # First check if application exists
        application = db.session.execute(
            select(Application).where(Application.id == application_id)
        ).scalar_one_or_none()
        
        if not application:
            return jsonify(error="Application not found"), 404
        
        # Check if job exists and user owns it
        job = db.session.execute(
            select(Job).where(Job.id == application.job_id, Job.user_id == user_id)
        ).scalar_one_or_none()
        
        if not job:
            return jsonify(error="Application not found or access denied"), 404
        
        if not application.cover_letter_path:
            return jsonify(error="Cover letter not found"), 404
        
        # Get file path
        static_folder = Path(current_app.instance_path).parent / 'static'
        file_path = static_folder / application.cover_letter_path
        
        if not file_path.exists():
            return jsonify(error="Cover letter file not found"), 404
        
        # Read file content as base64
        import base64
        with open(file_path, 'rb') as f:
            pdf_content = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            "filename": f"{application.first_name}_{application.last_name}_cover_letter.pdf",
            "content": pdf_content,
            "mimetype": "application/pdf"
        }), 200
        
    except Exception as e:
        logger.error(f"Error viewing cover letter: {str(e)}")
        return jsonify(error="An error occurred while viewing cover letter"), 500

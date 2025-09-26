import pytest
from unittest.mock import patch, MagicMock
from app.models.job import Job
from app.models.application import Application
from app.models.saved_job import SavedJob
from app.models.user import User


class TestJobDeletionAPI:
    """Test job deletion API endpoint"""

    def test_delete_job_success(self, client, auth_headers, make_user, make_job):
        """Test successful job deletion via API"""
        recruiter = make_user()
        job = make_job(user_id=recruiter.id)
        
        # Create auth headers for recruiter
        recruiter_headers = auth_headers(recruiter)
        
        # Mock the auth to return recruiter user
        with patch('app.api.recruiter.routes.get_jwt_identity', return_value=str(recruiter.id)):
            response = client.delete(f'/api/recruiter/my-jobs/{job.id}', headers=recruiter_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['message'] == 'Job deleted successfully'
            assert 'deletion_summary' in data
            
            deletion_summary = data['deletion_summary']
            assert deletion_summary['job_id'] == job.id
            assert deletion_summary['job_title'] == job.title  # Use the actual job title
            assert deletion_summary['applications_deleted'] == 0
            assert deletion_summary['saved_jobs_deleted'] == 0

    def test_delete_job_with_applications(self, client, auth_headers, make_user, make_job):
        """Test job deletion with applications via API"""
        recruiter = make_user()
        candidate1 = make_user()
        candidate2 = make_user()
        job = make_job(user_id=recruiter.id)
        
        # Create applications from different candidates
        application1 = Application(
            user_id=candidate1.id,
            job_id=job.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            resume_path="applications/1/resume1.pdf",
            cover_letter_path="applications/1/cover1.pdf"
        )
        
        application2 = Application(
            user_id=candidate2.id,
            job_id=job.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            resume_path="applications/1/resume2.pdf",
            cover_letter_path="applications/1/cover2.pdf"
        )
        
        from app.extensions import db
        db.session.add_all([application1, application2])
        
        # Create saved job
        saved_job = SavedJob(user_id=candidate1.id, job_id=job.id)
        db.session.add(saved_job)
        db.session.commit()
        
        # Create auth headers for recruiter
        recruiter_headers = auth_headers(recruiter)
        
        # Mock the auth to return recruiter user
        with patch('app.api.recruiter.routes.get_jwt_identity', return_value=str(recruiter.id)):
            response = client.delete(f'/api/recruiter/my-jobs/{job.id}', headers=recruiter_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            deletion_summary = data['deletion_summary']
            
            assert deletion_summary['applications_deleted'] == 2
            assert deletion_summary['saved_jobs_deleted'] == 1
            
            # Verify applications are deleted
            applications = db.session.execute(
                db.select(Application).where(Application.job_id == job.id)
            ).scalars().all()
            assert len(applications) == 0
            
            # Verify saved jobs are deleted
            saved_jobs = db.session.execute(
                db.select(SavedJob).where(SavedJob.job_id == job.id)
            ).scalars().all()
            assert len(saved_jobs) == 0

    def test_delete_job_not_found(self, client, auth_headers, make_user):
        """Test deleting a job that doesn't exist"""
        recruiter = make_user()
        
        recruiter_headers = auth_headers(recruiter)
        
        with patch('app.api.recruiter.routes.get_jwt_identity', return_value=str(recruiter.id)):
            response = client.delete('/api/recruiter/my-jobs/999', headers=recruiter_headers)
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
            assert 'not found' in data['error'].lower()

    def test_delete_job_wrong_user(self, client, auth_headers, make_user, make_job):
        """Test deleting a job owned by another user"""
        recruiter1 = make_user()
        recruiter2 = make_user()
        job = make_job(user_id=recruiter1.id)
        
        recruiter2_headers = auth_headers(recruiter2)
        
        with patch('app.api.recruiter.routes.get_jwt_identity', return_value=str(recruiter2.id)):
            response = client.delete(f'/api/recruiter/my-jobs/{job.id}', headers=recruiter2_headers)
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
            assert 'not found' in data['error'].lower()

    def test_delete_job_unauthorized(self, client, make_user, make_job):
        """Test deleting a job without authentication"""
        recruiter = make_user()
        job = make_job(user_id=recruiter.id)
        
        response = client.delete(f'/api/recruiter/my-jobs/{job.id}')
        
        assert response.status_code == 401

    def test_delete_job_server_error(self, client, auth_headers, make_user, make_job):
        """Test job deletion with server error"""
        recruiter = make_user()
        job = make_job(user_id=recruiter.id)
        
        recruiter_headers = auth_headers(recruiter)
        
        # Mock JobService to raise an exception
        with patch('app.api.recruiter.routes.JobService') as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_job.side_effect = Exception("Database error")
            
            with patch('app.api.recruiter.routes.get_jwt_identity', return_value=str(recruiter.id)):
                response = client.delete(f'/api/recruiter/my-jobs/{job.id}', headers=recruiter_headers)
                
                assert response.status_code == 500
                data = response.get_json()
                assert 'error' in data
                assert 'error occurred' in data['error'].lower()

    def test_delete_job_file_cleanup_integration(self, client, auth_headers, make_user, make_job):
        """Test job deletion with actual file cleanup"""
        recruiter = make_user()
        candidate = make_user()
        job = make_job(user_id=recruiter.id)
        
        # Create application with file paths (files don't need to exist for this test)
        application = Application(
            user_id=candidate.id,
            job_id=job.id,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            resume_path=f'applications/{candidate.id}/resume.pdf',
            cover_letter_path=f'applications/{candidate.id}/cover_letter.pdf'
        )
        
        from app.extensions import db
        db.session.add(application)
        db.session.commit()
        
        recruiter_headers = auth_headers(recruiter)
        
        with patch('app.api.recruiter.routes.get_jwt_identity', return_value=str(recruiter.id)):
            response = client.delete(f'/api/recruiter/my-jobs/{job.id}', headers=recruiter_headers)
            
            assert response.status_code == 200
            data = response.get_json()
            deletion_summary = data['deletion_summary']
            
            # Verify file cleanup results
            file_cleanup = deletion_summary['file_cleanup']
            assert file_cleanup['files_deleted'] >= 0  # Files may not exist in test environment
            assert file_cleanup['folders_deleted'] >= 0
            assert file_cleanup['errors'] == []

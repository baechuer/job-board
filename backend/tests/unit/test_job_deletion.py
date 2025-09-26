import pytest
from unittest.mock import patch, MagicMock
from app.services.job_service import JobService
from app.models.job import Job
from app.models.application import Application
from app.models.saved_job import SavedJob
from app.models.user import User


class TestJobDeletion:
    """Test job deletion functionality"""

    def test_delete_job_success(self, app, db, make_user):
        """Test successful job deletion with cleanup"""
        service = JobService()
        
        # Create a user
        user = make_user()
        user_id = user.id
        
        # Create a job
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "salary_min": 50000,
            "salary_max": 70000,
            "location": "Remote",
            "requirements": ["Python", "Flask"],
            "responsibilities": "Build APIs",
            "skills": ["Python", "Flask"],
            "application_deadline": "2025-12-31",
        }
        
        job_result = service.create_job(user_id, job_data)
        job_id = job_result["job"]["id"]
        
        # Mock file cleanup service
        with patch('app.services.job_service.FileCleanupService') as mock_cleanup_class:
            mock_cleanup_service = MagicMock()
            mock_cleanup_class.return_value = mock_cleanup_service
            mock_cleanup_service.cleanup_job_files.return_value = {
                'files_deleted': 2,
                'folders_deleted': 1,
                'errors': [],
                'deleted_paths': ['/path/to/file1.pdf', '/path/to/file2.pdf']
            }
            
            # Delete the job
            deletion_summary = service.delete_job(user_id, job_id)
            
            # Verify deletion summary
            assert deletion_summary['job_id'] == job_id
            assert deletion_summary['job_title'] == "Test Job"
            assert deletion_summary['applications_deleted'] == 0  # No applications
            assert deletion_summary['saved_jobs_deleted'] == 0  # No saved jobs
            assert deletion_summary['file_cleanup']['files_deleted'] == 2
            assert deletion_summary['file_cleanup']['folders_deleted'] == 1
            assert deletion_summary['errors'] == []
            
            # Verify file cleanup was called
            mock_cleanup_service.cleanup_job_files.assert_called_once_with(job_id)
            
            # Verify job is deleted from database
            job = db.session.get(Job, job_id)
            assert job is None

    def test_delete_job_with_applications(self, app, db, make_user):
        """Test job deletion with applications"""
        service = JobService()
        
        # Create a user
        user = make_user()
        user_id = user.id
        
        # Create a job
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "salary_min": 50000,
            "salary_max": 70000,
            "location": "Remote",
            "requirements": ["Python"],
            "responsibilities": "Build APIs",
            "skills": ["Python"],
            "application_deadline": "2025-12-31",
        }
        
        job_result = service.create_job(user_id, job_data)
        job_id = job_result["job"]["id"]
        
        # Create a candidate user
        candidate = make_user()
        
        # Create applications
        application1 = Application(
            user_id=candidate.id,
            job_id=job_id,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            resume_path="applications/1/resume1.pdf",
            cover_letter_path="applications/1/cover1.pdf"
        )
        
        # Create another candidate for the second application
        candidate2 = make_user()
        application2 = Application(
            user_id=candidate2.id,
            job_id=job_id,
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            resume_path="applications/2/resume2.pdf",
            cover_letter_path="applications/2/cover2.pdf"
        )
        
        db.session.add_all([application1, application2])
        db.session.commit()
        
        # Create saved job
        saved_job = SavedJob(user_id=candidate.id, job_id=job_id)
        db.session.add(saved_job)
        db.session.commit()
        
        # Mock file cleanup service
        with patch('app.services.job_service.FileCleanupService') as mock_cleanup_class:
            mock_cleanup_service = MagicMock()
            mock_cleanup_class.return_value = mock_cleanup_service
            mock_cleanup_service.cleanup_job_files.return_value = {
                'files_deleted': 4,  # 2 resumes + 2 cover letters
                'folders_deleted': 1,
                'errors': [],
                'deleted_paths': ['/path/to/file1.pdf', '/path/to/file2.pdf', '/path/to/file3.pdf', '/path/to/file4.pdf']
            }
            
            # Delete the job
            deletion_summary = service.delete_job(user_id, job_id)
            
            # Verify deletion summary
            assert deletion_summary['applications_deleted'] == 2
            assert deletion_summary['saved_jobs_deleted'] == 1
            assert deletion_summary['file_cleanup']['files_deleted'] == 4
            
            # Verify applications are deleted (CASCADE)
            applications = db.session.execute(
                db.select(Application).where(Application.job_id == job_id)
            ).scalars().all()
            assert len(applications) == 0
            
            # Verify saved jobs are deleted (CASCADE)
            saved_jobs = db.session.execute(
                db.select(SavedJob).where(SavedJob.job_id == job_id)
            ).scalars().all()
            assert len(saved_jobs) == 0

    def test_delete_job_not_found(self, app, db, make_user):
        """Test deleting a job that doesn't exist"""
        service = JobService()
        
        # Create a user
        user = make_user()
        user_id = user.id
        
        with pytest.raises(ValueError, match="Job not found or access denied"):
            service.delete_job(user_id, 999)

    def test_delete_job_wrong_user(self, app, db, make_user):
        """Test deleting a job owned by another user"""
        service = JobService()
        
        # Create first user
        user1 = make_user()
        user1_id = user1.id
        
        # Create a job
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "salary_min": 50000,
            "salary_max": 70000,
            "location": "Remote",
            "requirements": ["Python"],
            "responsibilities": "Build APIs",
            "skills": ["Python"],
            "application_deadline": "2025-12-31",
        }
        
        job_result = service.create_job(user1_id, job_data)
        job_id = job_result["job"]["id"]
        
        # Create another user
        user2 = make_user()
        user2_id = user2.id
        
        # Try to delete job as different user
        with pytest.raises(ValueError, match="Job not found or access denied"):
            service.delete_job(user2_id, job_id)

    def test_delete_job_database_error(self, app, db, make_user):
        """Test job deletion with database error"""
        service = JobService()
        
        # Create a user
        user = make_user()
        user_id = user.id
        
        # Create a job
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "salary_min": 50000,
            "salary_max": 70000,
            "location": "Remote",
            "requirements": ["Python"],
            "responsibilities": "Build APIs",
            "skills": ["Python"],
            "application_deadline": "2025-12-31",
        }
        
        job_result = service.create_job(user_id, job_data)
        job_id = job_result["job"]["id"]
        
        # Mock file cleanup service to succeed
        with patch('app.services.job_service.FileCleanupService') as mock_cleanup_class:
            mock_cleanup_service = MagicMock()
            mock_cleanup_class.return_value = mock_cleanup_service
            mock_cleanup_service.cleanup_job_files.return_value = {
                'files_deleted': 0,
                'folders_deleted': 0,
                'errors': [],
                'deleted_paths': []
            }
            
            # Mock database commit to raise an error
            with patch('app.services.job_service.db.session.commit') as mock_commit:
                with patch('app.services.job_service.db.session.rollback') as mock_rollback:
                    mock_commit.side_effect = Exception("Database error")
                    
                    with pytest.raises(Exception, match="Database error"):
                        service.delete_job(user_id, job_id)
                    
                    # Verify rollback was called
                    mock_rollback.assert_called()

    def test_delete_job_file_cleanup_error(self, app, db, make_user):
        """Test job deletion when file cleanup fails but job deletion succeeds"""
        service = JobService()
        
        # Create a user
        user = make_user()
        user_id = user.id
        
        # Create a job
        job_data = {
            "title": "Test Job",
            "description": "Test description",
            "salary_min": 50000,
            "salary_max": 70000,
            "location": "Remote",
            "requirements": ["Python"],
            "responsibilities": "Build APIs",
            "skills": ["Python"],
            "application_deadline": "2025-12-31",
        }
        
        job_result = service.create_job(user_id, job_data)
        job_id = job_result["job"]["id"]
        
        # Mock file cleanup service to return errors
        with patch('app.services.job_service.FileCleanupService') as mock_cleanup_class:
            mock_cleanup_service = MagicMock()
            mock_cleanup_class.return_value = mock_cleanup_service
            mock_cleanup_service.cleanup_job_files.return_value = {
                'files_deleted': 0,
                'folders_deleted': 0,
                'errors': ['File not found', 'Permission denied'],
                'deleted_paths': []
            }
            
            # Delete the job
            deletion_summary = service.delete_job(user_id, job_id)
            
            # Verify deletion succeeded despite file cleanup errors
            assert deletion_summary['job_id'] == job_id
            assert len(deletion_summary['file_cleanup']['errors']) == 2
            assert 'File not found' in deletion_summary['file_cleanup']['errors']
            assert 'Permission denied' in deletion_summary['file_cleanup']['errors']
            
            # Verify job is still deleted from database
            job = db.session.get(Job, job_id)
            assert job is None

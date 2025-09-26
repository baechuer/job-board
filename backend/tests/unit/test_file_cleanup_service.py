import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.services.file_cleanup_service import FileCleanupService
from app.models.application import Application
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.models.user import User


class TestFileCleanupService:
    """Test the FileCleanupService for job and user file cleanup"""

    @pytest.fixture
    def temp_static_folder(self):
        """Create a temporary static folder for testing"""
        temp_dir = tempfile.mkdtemp()
        static_folder = Path(temp_dir) / 'static'
        static_folder.mkdir()
        
        # Create subdirectories
        (static_folder / 'applications').mkdir()
        (static_folder / 'jobs').mkdir()
        
        yield static_folder
        
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_app_context(self, temp_static_folder):
        """Mock Flask app context with static folder"""
        with patch('app.services.file_cleanup_service.current_app') as mock_app:
            mock_app.instance_path = str(temp_static_folder.parent)
            yield mock_app
    
    @pytest.fixture
    def service_with_mocked_static(self, temp_static_folder):
        """Create FileCleanupService with mocked static folder"""
        with patch('app.services.file_cleanup_service.current_app') as mock_app:
            mock_app.instance_path = str(temp_static_folder.parent)
            service = FileCleanupService()
            # Override the static folder to use our test folder
            service.static_folder = temp_static_folder
            return service

    def test_cleanup_job_files_no_applications(self, mock_app_context, temp_static_folder):
        """Test cleanup when job has no applications"""
        service = FileCleanupService()
        
        # Mock database query to return no applications
        with patch('app.services.file_cleanup_service.db.session.execute') as mock_execute:
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = []
            mock_execute.return_value.scalars.return_value = mock_scalars
            
            result = service.cleanup_job_files(1)
            
            assert result['files_deleted'] == 0
            assert result['folders_deleted'] == 0
            assert result['errors'] == []

    def test_cleanup_job_files_with_applications(self, service_with_mocked_static, temp_static_folder):
        """Test cleanup when job has applications with files"""
        service = service_with_mocked_static
        
        # Create test files
        user_folder = temp_static_folder / 'applications' / '1'
        user_folder.mkdir(parents=True)
        
        resume_file = user_folder / 'resume_1.pdf'
        cover_letter_file = user_folder / 'cover_letter_1.pdf'
        
        resume_file.write_text('fake resume content')
        cover_letter_file.write_text('fake cover letter content')
        
        # Mock application with file paths
        mock_application = MagicMock()
        mock_application.user_id = 1
        mock_application.resume_path = 'applications/1/resume_1.pdf'
        mock_application.cover_letter_path = 'applications/1/cover_letter_1.pdf'
        
        # Mock database query
        with patch('app.services.file_cleanup_service.db.session.execute') as mock_execute:
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [mock_application]
            mock_execute.return_value.scalars.return_value = mock_scalars
            
            result = service.cleanup_job_files(1)
            
            assert result['files_deleted'] == 2
            assert result['folders_deleted'] == 1  # User folder should be deleted
            assert result['errors'] == []
            assert str(resume_file) in result['deleted_paths']
            assert str(cover_letter_file) in result['deleted_paths']
            
            # Verify files are actually deleted
            assert not resume_file.exists()
            assert not cover_letter_file.exists()
            assert not user_folder.exists()

    def test_cleanup_user_files(self, service_with_mocked_static, temp_static_folder):
        """Test cleanup of all files for a user"""
        service = service_with_mocked_static
        
        # Create test files
        user_folder = temp_static_folder / 'applications' / '1'
        user_folder.mkdir(parents=True)
        
        resume_file = user_folder / 'resume_1.pdf'
        cover_letter_file = user_folder / 'cover_letter_1.pdf'
        
        resume_file.write_text('fake resume content')
        cover_letter_file.write_text('fake cover letter content')
        
        # Mock applications
        mock_app1 = MagicMock()
        mock_app1.resume_path = 'applications/1/resume_1.pdf'
        mock_app1.cover_letter_path = 'applications/1/cover_letter_1.pdf'
        
        mock_app2 = MagicMock()
        mock_app2.resume_path = 'applications/1/resume_2.pdf'
        mock_app2.cover_letter_path = None
        
        # Create second resume file
        resume_file2 = user_folder / 'resume_2.pdf'
        resume_file2.write_text('fake resume content 2')
        
        # Mock database query
        with patch('app.services.file_cleanup_service.db.session.execute') as mock_execute:
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [mock_app1, mock_app2]
            mock_execute.return_value.scalars.return_value = mock_scalars
            
            result = service.cleanup_user_files(1)
            
            assert result['files_deleted'] == 3  # 2 resumes + 1 cover letter
            assert result['folders_deleted'] == 1  # User folder
            assert result['errors'] == []
            
            # Verify files are deleted
            assert not resume_file.exists()
            assert not resume_file2.exists()
            assert not cover_letter_file.exists()
            assert not user_folder.exists()

    def test_cleanup_orphaned_files(self, service_with_mocked_static, temp_static_folder):
        """Test cleanup of orphaned files"""
        service = service_with_mocked_static
        
        # Create orphaned files
        user_folder = temp_static_folder / 'applications' / '1'
        user_folder.mkdir(parents=True)
        
        orphaned_file = user_folder / 'orphaned.pdf'
        orphaned_file.write_text('orphaned content')
        
        # Mock applications with different file paths
        mock_application = MagicMock()
        mock_application.resume_path = 'applications/1/valid_resume.pdf'
        mock_application.cover_letter_path = 'applications/1/valid_cover.pdf'
        
        # Create valid files
        valid_resume = user_folder / 'valid_resume.pdf'
        valid_cover = user_folder / 'valid_cover.pdf'
        valid_resume.write_text('valid resume')
        valid_cover.write_text('valid cover')
        
        # Mock database query
        with patch('app.services.file_cleanup_service.db.session.execute') as mock_execute:
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = [mock_application]
            mock_execute.return_value.scalars.return_value = mock_scalars
            
            result = service.cleanup_orphaned_files()
            
            assert result['files_deleted'] == 1  # Only orphaned file
            assert result['folders_deleted'] == 0  # Folder not empty yet
            assert result['errors'] == []
            
            # Verify orphaned file is deleted but valid files remain
            assert not orphaned_file.exists()
            assert valid_resume.exists()
            assert valid_cover.exists()

    def test_get_storage_stats(self, service_with_mocked_static, temp_static_folder):
        """Test storage statistics calculation"""
        service = service_with_mocked_static
        
        # Create test files
        applications_folder = temp_static_folder / 'applications'
        jobs_folder = temp_static_folder / 'jobs'
        
        app_file = applications_folder / '1' / 'resume.pdf'
        app_file.parent.mkdir(parents=True)
        app_file.write_text('resume content')
        
        job_file = jobs_folder / '1' / 'job.pdf'
        job_file.parent.mkdir(parents=True)
        job_file.write_text('job content')
        
        other_file = temp_static_folder / 'other.pdf'
        other_file.write_text('other content')
        
        result = service.get_storage_stats()
        
        assert result['total_files'] == 3
        assert result['total_size_bytes'] > 0
        assert result['applications_folder_size'] > 0
        assert result['jobs_folder_size'] > 0
        assert result['other_files_size'] > 0

    def test_delete_file_nonexistent(self, mock_app_context, temp_static_folder):
        """Test deleting a file that doesn't exist"""
        service = FileCleanupService()
        
        nonexistent_file = temp_static_folder / 'nonexistent.pdf'
        result = service._delete_file(nonexistent_file)
        
        assert result is False

    def test_cleanup_empty_folder_nonexistent(self, mock_app_context, temp_static_folder):
        """Test cleaning up a folder that doesn't exist"""
        service = FileCleanupService()
        
        nonexistent_folder = temp_static_folder / 'nonexistent'
        result = service._cleanup_empty_folder(nonexistent_folder)
        
        assert result is False

    def test_cleanup_empty_folder_not_empty(self, mock_app_context, temp_static_folder):
        """Test cleaning up a folder that's not empty"""
        service = FileCleanupService()
        
        folder = temp_static_folder / 'not_empty'
        folder.mkdir()
        file_in_folder = folder / 'file.txt'
        file_in_folder.write_text('content')
        
        result = service._cleanup_empty_folder(folder)
        
        assert result is False
        assert folder.exists()  # Folder should still exist

    def test_error_handling_during_cleanup(self, mock_app_context, temp_static_folder):
        """Test error handling during cleanup"""
        service = FileCleanupService()
        
        # Mock database query to raise an exception
        with patch('app.services.file_cleanup_service.db.session.execute') as mock_execute:
            mock_execute.side_effect = Exception("Database error")
            
            result = service.cleanup_job_files(1)
            
            assert result['files_deleted'] == 0
            assert result['folders_deleted'] == 0
            assert len(result['errors']) == 1
            assert "Database error" in result['errors'][0]

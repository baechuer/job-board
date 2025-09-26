import pytest
import os
import tempfile
from datetime import date
from unittest.mock import patch, MagicMock
from io import BytesIO
from flask import current_app
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.services.application_service import ApplicationService
from app.config.testing import TestConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create a sample user"""
    with app.app_context():
        user = User(
            email='test@example.com',
            username='testuser',
            password_hash='hashed_password',
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def sample_job(app, sample_user):
    """Create a sample job"""
    with app.app_context():
        job = Job(
            user_id=sample_user.id,
            title='Software Engineer',
            description='A great job',
            salary_min=50000,
            salary_max=80000,
            location='San Francisco',
            requirements=['Python', 'JavaScript'],
            responsibilities='Write code',
            skills=['Python', 'JavaScript'],
            application_deadline=date(2024, 12, 31),
            employment_type='full_time',
            work_mode='remote'
        )
        db.session.add(job)
        db.session.commit()
        db.session.refresh(job)
        return job


@pytest.fixture
def sample_application_data():
    """Sample application data"""
    return {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'phone': '123-456-7890',
        'currentCompany': 'Tech Corp',
        'currentPosition': 'Developer',
        'experience': '3-5 years',
        'education': 'bachelor',
        'skills': 'Python, JavaScript, React',
        'portfolio': 'https://johndoe.com',
        'linkedin': 'https://linkedin.com/in/johndoe',
        'github': 'https://github.com/johndoe',
        'availability': 'Immediately',
        'salaryExpectation': '70000',
        'noticePeriod': '2 weeks',
        'workAuthorization': 'US Citizen',
        'relocation': 'Yes',
        'additionalInfo': 'Passionate about technology'
    }


class TestApplicationService:
    """Test cases for ApplicationService"""
    
    def test_validate_file_valid_pdf(self, app):
        """Test file validation with valid PDF"""
        with app.app_context():
            service = ApplicationService()
            
            # Create a mock PDF file
            mock_file = MagicMock()
            mock_file.content_type = 'application/pdf'
            mock_file.content_length = 1024 * 1024  # 1MB
            mock_file.filename = 'resume.pdf'
            
            # Should not raise exception for valid PDF
            try:
                service._validate_file(mock_file)
                assert True  # If no exception is raised, test passes
            except Exception as e:
                assert False, f"Valid PDF should not raise exception: {e}"
    
    def test_validate_file_invalid_type(self, app):
        """Test file validation with invalid file type"""
        with app.app_context():
            service = ApplicationService()
            
            # Create a mock non-PDF file
            mock_file = MagicMock()
            mock_file.content_type = 'text/plain'
            mock_file.filename = 'resume.txt'
            
            # Should raise ValidationError for invalid file type
            with pytest.raises(Exception):  # ValidationError
                service._validate_file(mock_file)
    
    def test_validate_file_too_large(self, app):
        """Test file validation with file too large"""
        with app.app_context():
            service = ApplicationService()
            
            # Create a mock file that's too large
            mock_file = MagicMock()
            mock_file.content_type = 'application/pdf'
            mock_file.content_length = 10 * 1024 * 1024  # 10MB
            mock_file.filename = 'large_resume.pdf'
            
            # Should raise ValidationError for file too large
            with pytest.raises(Exception):  # ValidationError
                service._validate_file(mock_file)
    
    def test_generate_file_path(self, app):
        """Test file path generation"""
        with app.app_context():
            service = ApplicationService()
            
            path = service._generate_file_path(1, 2, 'resume', 'test.pdf')
            
            # Check that path follows the expected structure
            path_str = str(path)
            assert 'users/1/applications/2/resume' in path_str.replace('\\', '/')
            assert path.suffix == '.pdf'
            # Check that it contains a UUID4 (36 characters)
            filename = path.stem
            assert len(filename) == 36  # UUID4 length
    
    @patch('app.services.application_service.ApplicationService._save_file')
    def test_create_application_success(self, mock_save_file, app, sample_user, sample_job, sample_application_data):
        """Test successful application creation"""
        with app.app_context():
            mock_save_file.return_value = True
            
            service = ApplicationService()
            
            # Create mock files
            resume_file = MagicMock()
            resume_file.content_type = 'application/pdf'
            resume_file.content_length = 1024 * 1024
            resume_file.filename = 'resume.pdf'
            
            cover_letter_file = MagicMock()
            cover_letter_file.content_type = 'application/pdf'
            cover_letter_file.content_length = 512 * 1024
            cover_letter_file.filename = 'cover_letter.pdf'
            
            result = service.create_application(
                user_id=sample_user.id,
                job_id=sample_job.id,
                application_data=sample_application_data,
                resume_file=resume_file,
                cover_letter_file=cover_letter_file
            )
            
            assert result['status'] == 'created'
            assert 'application' in result
            assert result['application']['job_id'] == sample_job.id
            
            # Verify application was saved to database
            application = Application.query.filter_by(user_id=sample_user.id, job_id=sample_job.id).first()
            assert application is not None
            assert application.first_name == sample_application_data['firstName']
            assert application.last_name == sample_application_data['lastName']
    
    def test_create_application_duplicate(self, app, sample_user, sample_job, sample_application_data):
        """Test application creation with duplicate application"""
        with app.app_context():
            # Create existing application
            existing_app = Application(
                user_id=sample_user.id,
                job_id=sample_job.id,
                first_name='Jane',
                last_name='Smith',
                email='jane@example.com',
                status='submitted'
            )
            db.session.add(existing_app)
            db.session.commit()
            
            service = ApplicationService()
            
            resume_file = MagicMock()
            resume_file.content_type = 'application/pdf'
            resume_file.content_length = 1024 * 1024
            resume_file.filename = 'resume.pdf'
            
            cover_letter_file = MagicMock()
            cover_letter_file.content_type = 'application/pdf'
            cover_letter_file.content_length = 512 * 1024
            cover_letter_file.filename = 'cover_letter.pdf'
            
            with pytest.raises(Exception):  # Should raise ConflictError
                service.create_application(
                    user_id=sample_user.id,
                    job_id=sample_job.id,
                    application_data=sample_application_data,
                    resume_file=resume_file,
                    cover_letter_file=cover_letter_file
                )
    
    def test_get_user_applications(self, app, sample_user, sample_job):
        """Test getting user applications"""
        with app.app_context():
            # Create test applications
            app1 = Application(
                user_id=sample_user.id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted'
            )
            db.session.add(app1)
            db.session.commit()
            
            service = ApplicationService()
            result = service.get_user_applications(sample_user.id)
            
            assert 'applications' in result
            assert 'pagination' in result
            assert len(result['applications']) == 1
            assert result['applications'][0]['job']['title'] == sample_job.title
    
    def test_get_job_applications(self, app, sample_user, sample_job):
        """Test getting job applications"""
        with app.app_context():
            # Create test application
            app1 = Application(
                user_id=sample_user.id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted'
            )
            db.session.add(app1)
            db.session.commit()
            
            service = ApplicationService()
            result = service.get_job_applications(sample_job.id, sample_job.user_id)
            
            assert 'applications' in result
            assert 'pagination' in result
            assert len(result['applications']) == 1
            assert result['applications'][0]['first_name'] == 'John'

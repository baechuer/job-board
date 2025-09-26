import pytest
import json
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
from app.models.user_role import UserRole
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
def auth_headers(app, sample_user):
    """Get authentication headers"""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        # Get the user ID from the database to avoid detached instance issues
        user_id = db.session.execute(
            db.select(User.id).where(User.email == 'test@example.com')
        ).scalar()
        token = create_access_token(identity=str(user_id))
        return {'Authorization': f'Bearer {token}'}


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
        
        # Add candidate role
        role = UserRole(user_id=user.id, role='candidate')
        db.session.add(role)
        db.session.commit()
        
        return user


@pytest.fixture
def sample_recruiter(app):
    """Create a sample recruiter"""
    with app.app_context():
        user = User(
            email='recruiter@example.com',
            username='recruiter',
            password_hash='hashed_password',
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        
        # Add recruiter role
        role = UserRole(user_id=user.id, role='recruiter')
        db.session.add(role)
        db.session.commit()
        
        return user


@pytest.fixture
def sample_job(app, sample_recruiter):
    """Create a sample job"""
    with app.app_context():
        # Get the recruiter ID from the database to avoid detached instance issues
        recruiter_id = db.session.execute(
            db.select(User.id).where(User.email == 'recruiter@example.com')
        ).scalar()
        
        job = Job(
            user_id=recruiter_id,
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


class TestApplicationAPI:
    """Integration tests for Application API endpoints"""
    
    @patch('app.services.application_service.ApplicationService._save_file')
    def test_apply_for_job_success(self, mock_save_file, client, auth_headers, sample_job, sample_application_data):
        """Test successful job application"""
        mock_save_file.return_value = True
        
        # Create test PDF files
        resume_content = b'%PDF-1.4 fake pdf content'
        cover_letter_content = b'%PDF-1.4 fake cover letter content'
        
        data = {
            'firstName': sample_application_data['firstName'],
            'lastName': sample_application_data['lastName'],
            'email': sample_application_data['email'],
            'phone': sample_application_data['phone'],
            'currentCompany': sample_application_data['currentCompany'],
            'currentPosition': sample_application_data['currentPosition'],
            'experience': sample_application_data['experience'],
            'education': sample_application_data['education'],
            'skills': sample_application_data['skills'],
            'portfolio': sample_application_data['portfolio'],
            'linkedin': sample_application_data['linkedin'],
            'github': sample_application_data['github'],
            'availability': sample_application_data['availability'],
            'salaryExpectation': sample_application_data['salaryExpectation'],
            'noticePeriod': sample_application_data['noticePeriod'],
            'workAuthorization': sample_application_data['workAuthorization'],
            'relocation': sample_application_data['relocation'],
            'additionalInfo': sample_application_data['additionalInfo'],
            'resume': (BytesIO(resume_content), 'resume.pdf'),
            'coverLetter': (BytesIO(cover_letter_content), 'cover_letter.pdf')
        }
        
        response = client.post(
            f'/api/applications/jobs/{sample_job.id}/apply',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'created'
        assert 'application' in data
    
    def test_apply_for_job_missing_files(self, client, auth_headers, sample_job, sample_application_data):
        """Test job application with missing files"""
        data = {
            'firstName': sample_application_data['firstName'],
            'lastName': sample_application_data['lastName'],
            'email': sample_application_data['email'],
        }
        
        response = client.post(
            f'/api/applications/jobs/{sample_job.id}/apply',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_apply_for_job_invalid_file_type(self, client, auth_headers, sample_job, sample_application_data):
        """Test job application with invalid file type"""
        # Create test text file (not PDF)
        text_content = b'This is not a PDF file'
        
        data = {
            'firstName': sample_application_data['firstName'],
            'lastName': sample_application_data['lastName'],
            'email': sample_application_data['email'],
            'resume': (BytesIO(text_content), 'resume.txt'),
            'coverLetter': (BytesIO(text_content), 'cover_letter.txt')
        }
        
        response = client.post(
            f'/api/applications/jobs/{sample_job.id}/apply',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'txt' in data['error'] or 'PDF' in data['error']
    
    def test_apply_for_job_duplicate(self, client, auth_headers, sample_job, sample_application_data):
        """Test duplicate job application"""
        # Create existing application
        with client.application.app_context():
            existing_app = Application(
                user_id=1,  # Assuming user ID 1 from auth
                job_id=sample_job.id,
                first_name='Jane',
                last_name='Smith',
                email='jane@example.com',
                status='submitted'
            )
            db.session.add(existing_app)
            db.session.commit()
        
        # Create test PDF files
        resume_content = b'%PDF-1.4 fake pdf content'
        cover_letter_content = b'%PDF-1.4 fake cover letter content'
        
        data = {
            'firstName': sample_application_data['firstName'],
            'lastName': sample_application_data['lastName'],
            'email': sample_application_data['email'],
            'resume': (BytesIO(resume_content), 'resume.pdf'),
            'coverLetter': (BytesIO(cover_letter_content), 'cover_letter.pdf')
        }
        
        response = client.post(
            f'/api/applications/jobs/{sample_job.id}/apply',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'already applied' in data['error'].lower()
    
    def test_get_my_applications(self, client, auth_headers, sample_job):
        """Test getting user's applications"""
        # Create test application
        with client.application.app_context():
            app = Application(
                user_id=1,  # Assuming user ID 1 from auth
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted'
            )
            db.session.add(app)
            db.session.commit()
        
        response = client.get(
            '/api/applications/my-applications',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data
        assert 'pagination' in data
        assert len(data['applications']) == 1
    
    def test_get_job_applications(self, client, auth_headers, sample_job, sample_user):
        """Test getting applications for a job (recruiter only)"""
        # Create test application
        with client.application.app_context():
            # Get user ID from database to avoid detached instance issues
            user_id = db.session.execute(
                db.select(User.id).where(User.email == 'test@example.com')
            ).scalar()
            
            app = Application(
                user_id=user_id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted'
            )
            db.session.add(app)
            db.session.commit()
        
        # Use recruiter's auth headers
        with client.application.app_context():
            from flask_jwt_extended import create_access_token
            recruiter_id = db.session.execute(
                db.select(User.id).where(User.email == 'recruiter@example.com')
            ).scalar()
            token = create_access_token(identity=str(recruiter_id))
            recruiter_headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get(
            f'/api/applications/jobs/{sample_job.id}/applications',
            headers=recruiter_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data
        assert 'pagination' in data
        assert len(data['applications']) == 1
        assert data['applications'][0]['first_name'] == 'John'
    
    def test_get_job_applications_unauthorized(self, client, auth_headers, sample_job, sample_user):
        """Test getting applications for a job without authorization"""
        # Create test application
        with client.application.app_context():
            # Get user ID from database to avoid detached instance issues
            user_id = db.session.execute(
                db.select(User.id).where(User.email == 'test@example.com')
            ).scalar()
            
            app = Application(
                user_id=user_id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted'
            )
            db.session.add(app)
            db.session.commit()
        
        # Try to access with candidate's auth headers (should fail)
        response = client.get(
            f'/api/applications/jobs/{sample_job.id}/applications',
            headers=auth_headers
        )
        
        # The API returns 403 error when user is not job owner
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_apply_for_job_unauthorized(self, client, sample_job, sample_application_data):
        """Test job application without authentication"""
        data = {
            'firstName': sample_application_data['firstName'],
            'lastName': sample_application_data['lastName'],
            'email': sample_application_data['email'],
        }
        
        response = client.post(
            f'/api/applications/jobs/{sample_job.id}/apply',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 401

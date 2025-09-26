import pytest
import json
from datetime import date
from unittest.mock import patch, MagicMock
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
def recruiter_auth_headers(app, sample_recruiter):
    """Get recruiter authentication headers"""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        recruiter_id = db.session.execute(
            db.select(User.id).where(User.email == 'recruiter@example.com')
        ).scalar()
        token = create_access_token(identity=str(recruiter_id))
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def candidate_auth_headers(app, sample_candidate):
    """Get candidate authentication headers"""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        candidate_id = db.session.execute(
            db.select(User.id).where(User.email == 'candidate@example.com')
        ).scalar()
        token = create_access_token(identity=str(candidate_id))
        return {'Authorization': f'Bearer {token}'}


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
def sample_candidate(app):
    """Create a sample candidate"""
    with app.app_context():
        user = User(
            email='candidate@example.com',
            username='candidate',
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
def sample_job(app, sample_recruiter):
    """Create a sample job"""
    with app.app_context():
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
            work_mode='remote',
            seniority='mid'
        )
        db.session.add(job)
        db.session.commit()
        db.session.refresh(job)
        return job


@pytest.fixture
def sample_application(app, sample_job, sample_candidate):
    """Create a sample application"""
    with app.app_context():
        candidate_id = db.session.execute(
            db.select(User.id).where(User.email == 'candidate@example.com')
        ).scalar()
        
        application = Application(
            user_id=candidate_id,
            job_id=sample_job.id,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='123-456-7890',
            current_company='Tech Corp',
            current_position='Developer',
            experience='3-5 years',
            education='bachelor',
            skills='Python, JavaScript, React',
            portfolio='https://johndoe.com',
            linkedin='https://linkedin.com/in/johndoe',
            github='https://github.com/johndoe',
            availability='Immediately',
            salary_expectation=70000,
            notice_period='2 weeks',
            work_authorization='US Citizen',
            relocation='Yes',
            additional_info='Passionate about technology',
            status='submitted',
            resume_path='resumes/john_doe_resume.pdf',
            cover_letter_path='cover_letters/john_doe_cover_letter.pdf'
        )
        db.session.add(application)
        db.session.commit()
        db.session.refresh(application)
        return application


class TestApplicationDetailAPI:
    """Integration tests for Application Detail API endpoint"""
    
    def test_get_application_detail_success(self, client, recruiter_auth_headers, sample_job, sample_candidate):
        """Test successful retrieval of application details"""
        # Create test application within the test
        with client.application.app_context():
            candidate_id = db.session.execute(
                db.select(User.id).where(User.email == 'candidate@example.com')
            ).scalar()
            
            application = Application(
                user_id=candidate_id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                phone='123-456-7890',
                current_company='Tech Corp',
                current_position='Developer',
                experience='3-5 years',
                education='bachelor',
                skills='Python, JavaScript, React',
                portfolio='https://johndoe.com',
                linkedin='https://linkedin.com/in/johndoe',
                github='https://github.com/johndoe',
                availability='Immediately',
                salary_expectation=70000,
                notice_period='2 weeks',
                work_authorization='US Citizen',
                relocation='Yes',
                additional_info='Passionate about technology',
                status='submitted',
                resume_path='resumes/john_doe_resume.pdf',
                cover_letter_path='cover_letters/john_doe_cover_letter.pdf'
            )
            db.session.add(application)
            db.session.commit()
            db.session.refresh(application)
            application_id = application.id
        
        response = client.get(
            f'/api/applications/{application_id}',
            headers=recruiter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check application data
        assert data['id'] == application_id
        assert data['first_name'] == 'John'
        assert data['last_name'] == 'Doe'
        assert data['email'] == 'john@example.com'
        assert data['phone'] == '123-456-7890'
        assert data['current_company'] == 'Tech Corp'
        assert data['current_position'] == 'Developer'
        assert data['experience'] == '3-5 years'
        assert data['education'] == 'bachelor'
        assert data['skills'] == 'Python, JavaScript, React'
        assert data['portfolio'] == 'https://johndoe.com'
        assert data['linkedin'] == 'https://linkedin.com/in/johndoe'
        assert data['github'] == 'https://github.com/johndoe'
        assert data['availability'] == 'Immediately'
        assert data['salary_expectation'] == '70000'
        assert data['notice_period'] == '2 weeks'
        assert data['work_authorization'] == 'US Citizen'
        assert data['relocation'] == 'Yes'
        assert data['additional_info'] == 'Passionate about technology'
        assert data['status'] == 'submitted'
        assert data['resume_path'] == 'resumes/john_doe_resume.pdf'
        assert data['cover_letter_path'] == 'cover_letters/john_doe_cover_letter.pdf'
        
        # Check job data
        assert 'job' in data
        assert data['job']['id'] == sample_job.id
        assert data['job']['title'] == 'Software Engineer'
        assert data['job']['location'] == 'San Francisco'
        assert data['job']['employment_type'] == 'full_time'
        assert data['job']['seniority'] == 'mid'
        assert data['job']['work_mode'] == 'remote'
        assert data['job']['salary_min'] == 50000
        assert data['job']['salary_max'] == 80000
        
        # Check timestamps
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_get_application_detail_not_found(self, client, recruiter_auth_headers):
        """Test getting application detail for non-existent application"""
        response = client.get(
            '/api/applications/99999',
            headers=recruiter_auth_headers
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_get_application_detail_unauthorized_candidate(self, client, candidate_auth_headers, sample_application):
        """Test that candidates cannot access application details"""
        response = client.get(
            f'/api/applications/{sample_application.id}',
            headers=candidate_auth_headers
        )
        
        assert response.status_code == 404  # Returns 404 instead of 403 for security
        data = response.get_json()
        assert 'error' in data
    
    def test_get_application_detail_unauthorized_recruiter(self, client, sample_application):
        """Test getting application detail without authentication"""
        response = client.get(f'/api/applications/{sample_application.id}')
        
        assert response.status_code == 401
    
    def test_get_application_detail_wrong_recruiter(self, client, sample_application):
        """Test that recruiter cannot access applications for jobs they don't own"""
        # Create another recruiter
        with client.application.app_context():
            other_recruiter = User(
                email='other@example.com',
                username='other',
                password_hash='hashed_password',
                is_verified=True
            )
            db.session.add(other_recruiter)
            db.session.commit()
            
            role = UserRole(user_id=other_recruiter.id, role='recruiter')
            db.session.add(role)
            db.session.commit()
            
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(other_recruiter.id))
            other_headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get(
            f'/api/applications/{sample_application.id}',
            headers=other_headers
        )
        
        assert response.status_code == 404  # Returns 404 instead of 403 for security
        data = response.get_json()
        assert 'error' in data
    
    def test_update_application_status_success(self, client, recruiter_auth_headers, sample_job, sample_candidate):
        """Test successful application status update"""
        # Create test application within the test
        with client.application.app_context():
            candidate_id = db.session.execute(
                db.select(User.id).where(User.email == 'candidate@example.com')
            ).scalar()
            
            application = Application(
                user_id=candidate_id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted'
            )
            db.session.add(application)
            db.session.commit()
            db.session.refresh(application)
            application_id = application.id
        
        response = client.patch(
            f'/api/applications/{application_id}/status',
            headers=recruiter_auth_headers,
            json={'status': 'accepted'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Application status updated successfully'
        assert data['application_id'] == application_id
        assert data['status'] == 'accepted'
    
    def test_update_application_status_invalid_status(self, client, recruiter_auth_headers, sample_application):
        """Test application status update with invalid status"""
        response = client.patch(
            f'/api/applications/{sample_application.id}/status',
            headers=recruiter_auth_headers,
            json={'status': 'invalid_status'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_update_application_status_with_notes(self, client, recruiter_auth_headers, sample_application):
        """Test application status update with notes"""
        response = client.patch(
            f'/api/applications/{sample_application.id}/status',
            headers=recruiter_auth_headers,
            json={
                'status': 'rejected',
                'notes': 'Not a good fit for the role',
                'feedback': 'We appreciate your interest but...'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Application status updated successfully'
        assert data['status'] == 'rejected'
    
    @patch('app.api.applications.routes.send_file')
    @patch('pathlib.Path.exists')
    def test_download_resume_success(self, mock_exists, mock_send_file, client, recruiter_auth_headers, sample_job, sample_candidate):
        """Test successful resume download"""
        mock_send_file.return_value = 'fake_file_content'
        mock_exists.return_value = True
        
        # Create test application within the test
        with client.application.app_context():
            candidate_id = db.session.execute(
                db.select(User.id).where(User.email == 'candidate@example.com')
            ).scalar()
            
            application = Application(
                user_id=candidate_id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted',
                resume_path='resumes/john_doe_resume.pdf'
            )
            db.session.add(application)
            db.session.commit()
            db.session.refresh(application)
            application_id = application.id
        
        response = client.get(
            f'/api/applications/{application_id}/resume',
            headers=recruiter_auth_headers
        )
        
        assert response.status_code == 200
        mock_send_file.assert_called_once()
    
    @patch('app.api.applications.routes.send_file')
    @patch('pathlib.Path.exists')
    def test_download_cover_letter_success(self, mock_exists, mock_send_file, client, recruiter_auth_headers, sample_job, sample_candidate):
        """Test successful cover letter download"""
        mock_send_file.return_value = 'fake_file_content'
        mock_exists.return_value = True
        
        # Create test application within the test
        with client.application.app_context():
            candidate_id = db.session.execute(
                db.select(User.id).where(User.email == 'candidate@example.com')
            ).scalar()
            
            application = Application(
                user_id=candidate_id,
                job_id=sample_job.id,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                status='submitted',
                cover_letter_path='cover_letters/john_doe_cover_letter.pdf'
            )
            db.session.add(application)
            db.session.commit()
            db.session.refresh(application)
            application_id = application.id
        
        response = client.get(
            f'/api/applications/{application_id}/cover-letter',
            headers=recruiter_auth_headers
        )
        
        assert response.status_code == 200
        mock_send_file.assert_called_once()
    
    def test_download_resume_not_found(self, client, recruiter_auth_headers, sample_application):
        """Test resume download when file doesn't exist"""
        # Update application to have no resume path
        with client.application.app_context():
            application = db.session.get(Application, sample_application.id)
            application.resume_path = None
            db.session.commit()
        
        response = client.get(
            f'/api/applications/{sample_application.id}/resume',
            headers=recruiter_auth_headers
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_download_cover_letter_not_found(self, client, recruiter_auth_headers, sample_application):
        """Test cover letter download when file doesn't exist"""
        # Update application to have no cover letter path
        with client.application.app_context():
            application = db.session.get(Application, sample_application.id)
            application.cover_letter_path = None
            db.session.commit()
        
        response = client.get(
            f'/api/applications/{sample_application.id}/cover-letter',
            headers=recruiter_auth_headers
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()

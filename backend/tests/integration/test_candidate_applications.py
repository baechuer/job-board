import pytest
from flask import current_app
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.user_role import UserRole
from app.common.security import hash_password
from app.config.testing import TestConfig
from datetime import date, datetime, UTC
from io import BytesIO


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
def sample_candidate(app):
    """Create a sample candidate user"""
    with app.app_context():
        password_hash = hash_password('Password123')
        user = User(
            email='candidate@example.com',
            username='candidate',
            password_hash=password_hash,
            is_verified=True,
            email_verified_at=datetime.now(UTC)
        )
        db.session.add(user)
        db.session.flush()
        
        role = UserRole(user_id=user.id, role='candidate')
        db.session.add(role)
        db.session.commit()
        
        return user


@pytest.fixture
def sample_recruiter(app):
    """Create a sample recruiter user"""
    with app.app_context():
        password_hash = hash_password('Password123')
        user = User(
            email='recruiter@example.com',
            username='recruiter',
            password_hash=password_hash,
            is_verified=True,
            email_verified_at=datetime.now(UTC)
        )
        db.session.add(user)
        db.session.flush()
        
        role = UserRole(user_id=user.id, role='recruiter')
        db.session.add(role)
        db.session.commit()
        
        return user


@pytest.fixture
def sample_job(app, sample_recruiter):
    """Create a sample job"""
    with app.app_context():
        # Get the recruiter ID from the database to avoid detached instance
        recruiter_id = db.session.execute(
            db.select(User.id).where(User.email == 'recruiter@example.com')
        ).scalar()
        
        job = Job(
            user_id=recruiter_id,
            title='Software Engineer',
            description='A great software engineering position',
            salary_min=80000,
            salary_max=120000,
            location='San Francisco, CA',
            requirements='Python, JavaScript',
            responsibilities='Develop software',
            skills='Python, JavaScript, React',
            application_deadline=date(2025, 12, 31),
            employment_type='full_time',
            seniority='mid',
            work_mode='remote',
            visa_sponsorship=False,
            work_authorization='US Citizen'
        )
        db.session.add(job)
        db.session.commit()
        
        # Return job ID to avoid detached instance issues
        return job.id


@pytest.fixture
def auth_headers_candidate(client, sample_candidate):
    """Get auth headers for candidate"""
    response = client.post('/api/auth/login', json={
        'email': 'candidate@example.com',
        'password': 'Password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def auth_headers_recruiter(client, sample_recruiter):
    """Get auth headers for recruiter"""
    response = client.post('/api/auth/login', json={
        'email': 'recruiter@example.com',
        'password': 'Password123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


class TestCandidateApplicationsAPI:
    """Test candidate applications functionality"""
    
    def test_get_my_applications_empty(self, client, auth_headers_candidate):
        """Test getting applications when user has none"""
        response = client.get('/api/applications/my-applications', headers=auth_headers_candidate)
        
        assert response.status_code == 200
        data = response.json
        assert 'applications' in data
        assert 'pagination' in data
        assert len(data['applications']) == 0
        assert data['pagination']['total'] == 0
    
    def test_get_my_applications_with_data(self, client, auth_headers_candidate, sample_job):
        """Test getting applications when user has applications"""
        # First, create an application
        application_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'candidate@example.com',
            'phone': '1234567890',
            'experience': '0-1 years',
            'education': 'bachelor',
            'skills': 'Python, JavaScript',
            'salaryExpectation': '90000',
            'noticePeriod': '2 weeks',
            'workAuthorization': 'US Citizen',
            'relocation': 'Yes',
            'availability': 'Immediately',
            'additionalInfo': 'I am excited about this opportunity'
        }
        
        # Create test files
        resume_content = b'%PDF-1.4 fake pdf content'
        cover_letter_content = b'%PDF-1.4 fake cover letter content'
        
        response = client.post(
            f'/api/applications/jobs/{sample_job}/apply',
            headers=auth_headers_candidate,
            data={
                **application_data,
                'resume': (BytesIO(resume_content), 'resume.pdf'),
                'coverLetter': (BytesIO(cover_letter_content), 'cover_letter.pdf')
            }
        )
        
        assert response.status_code == 201
        
        # Now test getting applications
        response = client.get('/api/applications/my-applications', headers=auth_headers_candidate)
        
        assert response.status_code == 200
        data = response.json
        assert 'applications' in data
        assert 'pagination' in data
        assert len(data['applications']) == 1
        assert data['applications'][0]['first_name'] == 'John'
        assert data['applications'][0]['last_name'] == 'Doe'
        assert data['applications'][0]['email'] == 'candidate@example.com'
        assert data['applications'][0]['job']['title'] == 'Software Engineer'
        assert data['pagination']['total'] == 1
    
    def test_get_my_applications_pagination(self, client, auth_headers_candidate, sample_job):
        """Test pagination for applications"""
        # Create multiple jobs first
        jobs = []
        for i in range(5):
            # Get the recruiter ID from the database
            recruiter_id = db.session.execute(
                db.select(User.id).where(User.email == 'recruiter@example.com')
            ).scalar()
            
            job = Job(
                user_id=recruiter_id,
                title=f'Software Engineer {i}',
                description=f'A great software engineering position {i}',
                salary_min=80000,
                salary_max=120000,
                location='San Francisco, CA',
                requirements='Python, JavaScript',
                responsibilities='Develop software',
                skills='Python, JavaScript, React',
                application_deadline=date(2025, 12, 31),
                employment_type='full_time',
                seniority='mid',
                work_mode='remote',
                visa_sponsorship=False,
                work_authorization='US Citizen'
            )
            db.session.add(job)
            db.session.flush()
            jobs.append(job.id)
        
        db.session.commit()
        
        # Create multiple applications for different jobs
        names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie']
        
        for i in range(5):
            application_data = {
                'firstName': names[i],
                'lastName': 'Doe',
                'email': 'candidate@example.com',
                'phone': '1234567890',
                'experience': '0-1 years',
                'education': 'bachelor',
                'skills': 'Python, JavaScript',
                'salaryExpectation': '90000',
                'noticePeriod': '2 weeks',
                'workAuthorization': 'US Citizen',
                'relocation': 'Yes',
                'availability': 'Immediately',
                'additionalInfo': f'Application {i}'
            }
            
            resume_content = f'%PDF-1.4 fake resume content {i}'.encode()
            cover_letter_content = f'%PDF-1.4 fake cover letter content {i}'.encode()
            
            response = client.post(
                f'/api/applications/jobs/{jobs[i]}/apply',
                headers=auth_headers_candidate,
                data={
                    **application_data,
                    'resume': (BytesIO(resume_content), f'resume_{i}.pdf'),
                    'coverLetter': (BytesIO(cover_letter_content), f'cover_letter_{i}.pdf')
                }
            )
            
            assert response.status_code == 201
        
        # Test first page
        response = client.get('/api/applications/my-applications?page=1&per_page=3', headers=auth_headers_candidate)
        
        assert response.status_code == 200
        data = response.json
        assert len(data['applications']) == 3
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 3
        assert data['pagination']['total'] == 5
        assert data['pagination']['pages'] == 2
        
        # Test second page
        response = client.get('/api/applications/my-applications?page=2&per_page=3', headers=auth_headers_candidate)
        
        assert response.status_code == 200
        data = response.json
        assert len(data['applications']) == 2
        assert data['pagination']['page'] == 2
    
    def test_get_my_applications_filter_by_status(self, client, auth_headers_candidate, sample_job):
        """Test filtering applications by status"""
        # Create applications with different statuses
        application_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'candidate@example.com',
            'phone': '1234567890',
            'experience': '0-1 years',
            'education': 'bachelor',
            'skills': 'Python, JavaScript',
            'salaryExpectation': '90000',
            'noticePeriod': '2 weeks',
            'workAuthorization': 'US Citizen',
            'relocation': 'Yes',
            'availability': 'Immediately',
            'additionalInfo': 'Test application'
        }
        
        resume_content = b'%PDF-1.4 fake pdf content'
        cover_letter_content = b'%PDF-1.4 fake cover letter content'
        
        # Create application
        response = client.post(
            f'/api/applications/jobs/{sample_job}/apply',
            headers=auth_headers_candidate,
            data={
                **application_data,
                'resume': (BytesIO(resume_content), 'resume.pdf'),
                'coverLetter': (BytesIO(cover_letter_content), 'cover_letter.pdf')
            }
        )
        
        assert response.status_code == 201
        
        # Test filtering by status
        response = client.get('/api/applications/my-applications?status=submitted', headers=auth_headers_candidate)
        
        assert response.status_code == 200
        data = response.json
        assert len(data['applications']) == 1
        assert data['applications'][0]['status'] == 'submitted'
        
        # Test filtering by non-existent status
        response = client.get('/api/applications/my-applications?status=accepted', headers=auth_headers_candidate)
        
        assert response.status_code == 200
        data = response.json
        assert len(data['applications']) == 0
    
    def test_get_my_applications_unauthorized(self, client):
        """Test getting applications without authentication"""
        response = client.get('/api/applications/my-applications')
        
        assert response.status_code == 401
    
    def test_get_my_applications_invalid_pagination(self, client, auth_headers_candidate):
        """Test invalid pagination parameters"""
        # Test negative page
        response = client.get('/api/applications/my-applications?page=-1', headers=auth_headers_candidate)
        assert response.status_code == 400
        
        # Test zero page
        response = client.get('/api/applications/my-applications?page=0', headers=auth_headers_candidate)
        assert response.status_code == 400
        
        # Test invalid per_page
        response = client.get('/api/applications/my-applications?per_page=0', headers=auth_headers_candidate)
        assert response.status_code == 400
        
        # Test too large per_page
        response = client.get('/api/applications/my-applications?per_page=101', headers=auth_headers_candidate)
        assert response.status_code == 400


class TestRecruiterJobApplicationsAPI:
    """Test recruiter viewing job applications"""
    
    def test_get_job_applications_as_recruiter(self, client, auth_headers_recruiter, sample_job, sample_candidate):
        """Test recruiter getting applications for their job"""
        # First, create an application from a candidate
        application_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'candidate@example.com',
            'phone': '1234567890',
            'experience': '0-1 years',
            'education': 'bachelor',
            'skills': 'Python, JavaScript',
            'salaryExpectation': '90000',
            'noticePeriod': '2 weeks',
            'workAuthorization': 'US Citizen',
            'relocation': 'Yes',
            'availability': 'Immediately',
            'additionalInfo': 'Test application'
        }
        
        resume_content = b'%PDF-1.4 fake pdf content'
        cover_letter_content = b'%PDF-1.4 fake cover letter content'
        
        # Login as candidate and create application
        candidate_login = client.post('/api/auth/login', json={
            'email': 'candidate@example.com',
            'password': 'Password123'
        })
        candidate_token = candidate_login.json['access_token']
        candidate_headers = {'Authorization': f'Bearer {candidate_token}'}
        
        response = client.post(
            f'/api/applications/jobs/{sample_job}/apply',
            headers=candidate_headers,
            data={
                **application_data,
                'resume': (BytesIO(resume_content), 'resume.pdf'),
                'coverLetter': (BytesIO(cover_letter_content), 'cover_letter.pdf')
            }
        )
        
        assert response.status_code == 201
        
        # Now test recruiter getting applications for their job
        response = client.get(f'/api/applications/jobs/{sample_job}/applications', headers=auth_headers_recruiter)
        
        assert response.status_code == 200
        data = response.json
        assert 'applications' in data
        assert 'pagination' in data
        assert len(data['applications']) == 1
        assert data['applications'][0]['first_name'] == 'John'
        assert data['applications'][0]['last_name'] == 'Doe'
        assert data['applications'][0]['email'] == 'candidate@example.com'
    
    def test_get_job_applications_unauthorized(self, client, sample_job):
        """Test getting job applications without authentication"""
        response = client.get(f'/api/applications/jobs/{sample_job}/applications')
        
        assert response.status_code == 401
    
    def test_get_job_applications_not_job_owner(self, client, auth_headers_candidate, sample_job):
        """Test getting job applications when not the job owner"""
        response = client.get(f'/api/applications/jobs/{sample_job}/applications', headers=auth_headers_candidate)
        
        # Should return 403 or 404 depending on implementation
        assert response.status_code in [403, 404]

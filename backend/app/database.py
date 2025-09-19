from .models import *
from .security import *
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def drop_all(app):
    """Drops all tables to reset the database."""
    with app.app_context():
        db.drop_all()

### User functions
# Create User
def get_rolename(userrole):
    for role in Roles:
        if userrole == role.value:
            return role.name

def create_user(username, password, userrole, email):
    if get_user_by_username('admin') is not None and userrole == 1:
        return False
    user = User(username=username, password=password, userrole=userrole, email=email)
    db.session.add(user)
    db.session.commit()

    return user
def get_user_by_email(email):
    """Get a user by email."""
    return User.query.filter_by(email=email).first()

# Get User by ID
def get_user_by_username(username):
    """Get a user by username."""
    return User.query.filter_by(username=username).first()

# Update User
def update_user_password(username, password, new_password):
    """Update a user's password."""
    user = get_user_by_username(username)
    if user is None:
        return False
    if user.password == password:
        user.password = new_password
        db.session.commit()
        return True
    return False

# Update User Role
def update_userrole(username, userrole):
    """Update a user's role."""
    user = get_user_by_username(username)
    if user is None:
        return False
    user.userrole = userrole
    db.session.commit()
    return True

# Get All Users
def get_all_users():
    """Get all users."""
    return User.query.all()

def get_posted_job(title, company, location):
    return Job.query.filter_by(title=title, company=company, location=location).first()

def to_post_job(title, description, company, location, salary, company_id):
    job = Job(title=title, description=description, company=company, location=location, salary=salary, company_id=company_id)
    db.session.add(job)
    db.session.commit()

def get_all_jobs():
    return Job.query.order_by(Job.post_time.desc()).all()

def search_jobs(search_field, search):
    if search_field not in ['title', 'description', 'company', 'location']:
        raise ValueError("Invalid search")
    
    column = getattr(Job, search_field)
    search_term = f"%{search}%"
    return Job.query.filter(column.ilike(search_term)).order_by(Job.post_time.desc()).all()

def search_user_jobs(search_field, search, company_id):
    if search_field not in ['title', 'description', 'company', 'location']:
        raise ValueError("Invalid search")
    
    column = getattr(Job, search_field)
    search_term = f"%{search}%"
    return Job.query.filter(column.ilike(search_term), Job.company_id == company_id).order_by(Job.post_time.desc()).all()

def get_job_byid(id):
    return Job.query.filter_by(id=id).first()

def create_job_application(job_id, username, filepath):
    job_application = JobApplication(
        job_id=job_id,
        username=username,
        resume_filename=filepath
    )
    db.session.add(job_application)
    db.session.commit()

def get_posted_job_byuser(user_id):
    return Job.query.filter_by(company_id=user_id)

def get_applications_by_job_id(job_id):
    awaiting = JobApplication.query.filter_by(job_id=job_id, status=1).order_by(JobApplication.apply_date.desc()).all()
    approved = JobApplication.query.filter_by(job_id=job_id, status=2).order_by(JobApplication.apply_date.desc()).all()
    rejected = JobApplication.query.filter_by(job_id=job_id, status=3).order_by(JobApplication.apply_date.desc()).all()
    return awaiting + approved + rejected

def get_applications_by_application_id(application_id):
    return JobApplication.query.filter_by(id=application_id).first()

def search_applications(job_id, search_field, search):
    all_search_fields = ['all', 'await', 'approved', 'rejected']
    if search_field not in all_search_fields:
        raise ValueError("Invalid search")
    search_term = search.split(" ")
    if search_field == 'all':
        if len(search_term) == 1:
            return JobApplication.query.filter(JobApplication.job_id == job_id, JobApplication.firstname.like(f"%{search_term[0]}%")).order_by(JobApplication.apply_date.desc()).all()
        else:
            return JobApplication.query.filter(JobApplication.job_id == job_id, JobApplication.firstname.like(f"%{search_term[0]}%"), JobApplication.lastname.like(f"%{search_term[1]}%")).order_by(JobApplication.apply_date.desc()).all()
    else:
        if len(search_term) == 1:
            return JobApplication.query.filter(JobApplication.job_id == job_id, JobApplication.firstname.like(f"%{search_term[0]}%"), JobApplication.status == all_search_fields.index(search_field)).order_by(JobApplication.apply_date.desc()).all()
        else:
            return JobApplication.query.filter(JobApplication.job_id == job_id, JobApplication.firstname.like(f"%{search_term[0]}%"), JobApplication.lastname.like(f"%{search_term[1]}%"), JobApplication.status == all_search_fields.index(search_field)).order_by(JobApplication.apply_date.desc()).all()
def validate_user_view_job(job_id, current_user):
    job = Job.query.filter_by(id=job_id).first()
    if job.company_id != current_user.id:
        return False
    return True

def response_to_application(application_id, action):
    application = get_applications_by_application_id(application_id)
    if action == 'approve':
        application.status = 2
    elif action == 'reject':
        application.status = 3
    db.session.add(application)
    db.session.commit()
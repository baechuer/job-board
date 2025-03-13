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

def to_post_job(title, description, company, location, salary):
    job = Job(title=title, description=description, company=company, location=location, salary=salary)
    db.session.add(job)
    db.session.commit()

def get_all_jobs():
    return Job.query.all()

def search_jobs(search):
    search_term = f"%{search}%"
    return Job.query.filter(Job.title.like(search_term)).all()
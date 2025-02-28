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
def create_user(username, password, userrole):
    """Create a new user in the database."""
    user = User(username=username, password=password, userrole=userrole)
    db.session.add(user)
    db.session.commit()

    return user

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
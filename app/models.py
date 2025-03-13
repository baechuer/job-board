from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class Roles(Enum):
    ADMIN = 1
    USER = 2
    EMPLOYER = 3

class Status(Enum):
    AWAIT = 1
    APPROVED = 2
    REJECTED = 3

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password = db.Column(db.String(500), nullable = False)
    ### 1 = admin, 2 = user, 3 = employer
    userrole = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    is_active = db.Column(db.Boolean, default=True)
    verified = db.Column(db.Boolean, default=False)
    
    def set_active(self, active):
        self.is_active = active
    def json(self):
        return {'id': self.id, 'username':self.username, 'userrole':self.userrole}
    
    def set_password(self, password):
        self.password = password

class Job(db.Model):
    __tablename__ = 'Job'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40), nullable = False)
    description = db.Column(db.String(500), nullable = False)
    company = db.Column(db.String(40), nullable = False)
    location = db.Column(db.String(60), nullable = False)
    salary = db.Column(db.Numeric(precision=20, scale=2), nullable = False)

    __table_args__ = (
        db.UniqueConstraint('title', 'company', 'location'),
    )

class Application(db.Model):
    title = db.Column(db.String(40), nullable = False)
    company = db.Column(db.String(40), nullable = False)
    location = db.Column(db.String(60), nullable = False)
    username = db.Column(db.String(80), unique = True, nullable = False)
    status = db.Column(db.Integer, nullable = False)
    __table_args__ = (
        db.PrimaryKeyConstraint('title', 'company', 'location', 'username'),
        db.ForeignKeyConstraint(
            ['title', 'company', 'location'],
            ['Job.title', 'Job.company', 'Job.location']
        )
    )
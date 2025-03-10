from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class Roles(Enum):
    ADMIN = 1
    USER = 2
    EMPLOYER = 3
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
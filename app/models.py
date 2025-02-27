from enum import Enum
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Roles(Enum):
    ADMIN = 1
    USER = 2
    
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password = db.Column(db.String(80), nullable = False)
    ### 1 = admin, 2 = user
    userrole = db.Column(db.Integer, nullable = False)
    ### Password Salt
    salt = db.Column(db.String(5), nullable = False)

    def json(self):
        return {'id': self.id, 'username':self.username, 'userrole':self.userrole}
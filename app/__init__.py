from flask import Flask
from os import environ
from .database import init_db
def create_app(Testing=False):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
    if Testing:
        app.config["TESTING"] = True
    init_db(app)

    return app
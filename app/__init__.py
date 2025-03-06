from flask import Flask
from os import environ
from .database import init_db
def create_app(Testing=False):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
    app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
    app.config['MAIL_SERVER'] = environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = 587  # For SSL
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = environ.get("MAIL_USERNAME")  # Your email address
    app.config['MAIL_PASSWORD'] = environ.get("MAIL_PASSWORD")  # Your email password (or app-specific password)
    app.config['MAIL_DEFAULT_SENDER'] = environ.get("MAIL_USERNAME")  # Default sender for all emails
    if Testing:
        app.config["TESTING"] = True
    init_db(app)

    return app
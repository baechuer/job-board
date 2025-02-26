from flask import Flask, request, jsonify, render_template
from os import environ
from models import db, User, Roles

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db.init_app(app)

with app.app_context():
    db.create_all()
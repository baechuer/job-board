from flask import Flask, request, jsonify, render_template, make_response
from os import environ
from .database import *
from .models import db, User
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
init_db(app)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/users', methods=['POST'])
def create_user_route():
    try:
        data = request.get_json()
        create_user(data['username'], data['password'], data['userrole'], data['salt'])
        return make_response(jsonify({'message': 'User created!'}), 201)
    except:
        return make_response(jsonify({'message': 'Error creating user!'}), 500)

#get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = get_all_users()
        return make_response(jsonify({'users' : [user.json() for user in users]}), 200)
    except:
        return make_response(jsonify({'message': 'error fetching users'}), 500)
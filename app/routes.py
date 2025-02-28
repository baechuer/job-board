from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for, Blueprint, flash
from .database import *
from .models import db, User
import logging
from app import create_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()
page = {}

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#App Routes
@app.route('/')
def index():
    page["title"] = "Home"
    return render_template('index.html', page=page)

#Login and Register
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    page["title"] = "Login"
    return render_template('login.html', form=form, page=page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user is not None:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data)
        create_user(form.username.data, hashed_password, 1)
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    page["title"] = "Register"
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Welcome, {current_user.username}! <a href="{url_for("logout")}">Logout</a>'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/users', methods=['POST', 'GET'])
def users():
    # Create a new user
    if request.method == 'POST':
        try:
            data = request.get_json()
            create_user(data['username'], data['password'], data['userrole'], data['salt'])
            return make_response(jsonify({'message': 'User created!'}), 201)
        except:
            return make_response(jsonify({'message': 'Error creating user!'}), 500)
        
    # Get all users
    elif request.method == 'GET':
        try:
            users = get_all_users()
            return make_response(jsonify({'users' : [user.json() for user in users]}), 200)
        except:
            return make_response(jsonify({'message': 'error fetching users'}), 500)
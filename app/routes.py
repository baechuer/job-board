from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for, flash, session
from .database import *
from .models import db, User
import logging
from app import create_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm
from .security import *
from flask_mail import Message, Mail

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()
page = {}

login_manager = LoginManager(app)
login_manager.login_view = 'login'

serialiser = URLSafeTimedSerializer(app.config['SECRET_KEY'])
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_default_user():
    if not get_user_by_username("admin"):
        default_user = User(
            username='admin',
            password=generate_password_hash('admin'),
            userrole=1,
            email="someemail@email.com",
            verified=True
        )
        db.session.add(default_user)
        db.session.commit()

        default_user = User(
            username='abc',
            password=generate_password_hash('abc'),
            userrole=2,
            email="someemail1@email.com",
            verified=True
        )
        db.session.add(default_user)
        db.session.commit()
        print("✅ Default admin user created.")
    else:
        print("ℹ️ Default admin user already exists.")
with app.app_context():
    create_default_user()
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
            if not user.verified:
                flash('Please verify your email before logging in.', 'danger')
                return redirect(url_for('login'))
            login_user(user)
            session['logged_in'] = True
            session['username'] = form.username.data
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
        if get_user_by_email(form.email.data) is not None:
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)

        if not create_user(form.username.data, hashed_password, form.userrole.data, form.email.data):
            flash('Error happening when creating user', 'danger')
            return redirect(url_for('register'))
        user = get_user_by_username(form.username.data)
        send_verification_email(user, serialiser)
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
    page["title"] = "Register"
    return render_template('register.html', form=form, page=page)

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Welcome, {current_user.username}! <a href="{url_for("logout")}">Logout</a>'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    session.pop('username', None)
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
        

#Email Verification:
def send_verification_email(user, serialiser):
    token = generate_verification_token(user.email, serialiser)
    verify_url = url_for('verify_email', token=token, _external=True)
    try:
        msg = Message('Verify your email',
                    recipients=[user.email],
                    sender=app.config['MAIL_USERNAME'],
                    body=f'Click the link to verify your email: {verify_url}'
                )
        mail.send(msg)
    except Exception as e:
        flash(f'Error sending email: {str(e)}', 'danger')  # Optional: Show error message
        print(f"Error sending email: {str(e)}") 

@app.route('/verify_email/<token>')
def verify_email(token):
    email = verify_token(token, serialiser=serialiser)
    if email is None:
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    user = get_user_by_email(email)
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))
    if user.verified:
        flash('Account already verified.', 'info')
    else:
        user.verified = True
        db.session.commit()
        flash('Email verified! You can now log in.', 'success')
    return redirect(url_for('login'))
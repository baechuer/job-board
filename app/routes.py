from flask import request, jsonify, render_template, make_response, redirect, url_for, flash, session, send_from_directory
from .database import *
from .models import db, User
import logging
from app import create_app
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import *
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

        default_user1 = User(
            username='abc',
            password=generate_password_hash('abc'),
            userrole=2,
            email="someemail1@email.com",
            verified=True       
        )
        db.session.add(default_user1)

        default_user1 = User(
            username='firm',
            password=generate_password_hash('firm'),
            userrole=3,
            email="someemail2@email.com",
            verified=True       
        )
        db.session.add(default_user1)
        db.session.commit()

        default_job = Job(
            id = 1,
            title = "Software Engineer",
            description = "This is some description",
            company = "Some Company",
            location = "Some location",
            salary = 100000.0,
            post_time = datetime(2024, 1, 1, 10, 30, 0),
            company_id = default_user.id,

        )
        db.session.add(default_job)

        default_application = JobApplication(
            job_id=default_job.id,
            username = 'abc',
            resume_filename = "Payment_information_S345444665.pdf",
            firstname = 'ABC',
            lastname = 'ABC'
        )
        db.session.add(default_application)
        db.session.commit()

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

@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    #Searching
    
    reference_time = datetime.now()  # Current time as reference
    page['title'] = 'Dashboard'
    if request.method == 'POST':
        try:
            jobs = search_jobs(request.form.get("search-field"), request.form.get("some_input"))
        except:
            flash("Invalid search term")
            redirect(url_for("dashboard"))
    else:
        jobs = get_all_jobs()
    return render_template('dashboard.html', page=page, role=get_rolename(current_user.userrole), jobs=jobs, reference_time=reference_time)

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

@app.route('/verify_email/<token>', methods=["GET"])
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

#Changing password
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    page["title"] = "Reset Password"
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email(email)
        if user:
            token = serialiser.dumps(user.email, salt='password-reset')
            reset_link = url_for('reset_password', token=token, _external=True)
            # Send email with the reset link
            msg = Message('Reset Password',
                        recipients=[user.email],
                        sender=app.config['MAIL_USERNAME'],
                        body=f'Click the link to reset your password: {reset_link}'
                    )
            mail.send(msg)
        flash('If your email is in our system, a reset link has been sent.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', page=page)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    page["title"] = "Entering New Password"
    try:
        email = serialiser.loads(token, salt='password-reset', max_age=3600)  # 1 hour expiry
    except Exception:
        flash('The password reset link is invalid or expired.')
        return redirect(url_for('reset_password_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if form.new_password.data != form.new_password_repeat.data:
            flash("Please repeat your password", "danger")
            return render_template('reset_password.html', form=form, page=page)
        user = get_user_by_email(email)
        user.set_password(generate_password_hash(form.new_password.data))  # assuming you have a method like this
        db.session.commit()
        flash('Your password has been updated.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, page=page)

@login_required
@app.route('/post_job', methods=['POST', 'GET'])
def post_job():
    if current_user.userrole == 2:
        flash('You do not have access to post jobs.')
        return redirect(url_for('dashboard'))
    form = JobPostForm()
    #Post Request
    if form.validate_on_submit():
        if get_posted_job(form.title.data, form.company.data, form.location.data) is not None:
            flash("Already posted this job")
            return redirect(url_for('post_job'))
        to_post_job(form.title.data, form.description.data, form.company.data, form.location.data, form.salary.data, current_user.id)
        flash("Successfully posted the job.")
        return redirect(url_for('dashboard'))
    #Get Request
    page['title'] = 'Post Job'
    return render_template('post_job.html', page=page, form=form, role=get_rolename(current_user.userrole))

@login_required
@app.route('/apply_job/<int:job_id>', methods = ['POST', 'GET'])
def apply_job(job_id):
    page['title'] = 'apply_job'
    form = JobApplyForm()

    job = get_job_byid(job_id)
    if job is None:
        flash("Job does not exists")
        return redirect(url_for('dashboard'))
    elif current_user.userrole == 3:
        flash("Employers are not permitted to apply for job")
        return redirect(url_for('dashboard'))

    if form.validate_on_submit():
        file = form.resume.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)  # Save the file to the specified directory
            create_job_application(job_id, current_user.username, form.firstname.data, form.lastname.data, filename)

            flash("Your application has been submitted successfully.")
            return redirect(url_for("dashboard"))
    return render_template('apply_job.html', page=page, form=form)

@login_required
@app.route('/view_posted_job', methods = ['POST', 'GET'])
def view_posted_job():
    if current_user.userrole == 2:
        flash("You are not permitted to post or view your posted jobs")
        return redirect(url_for('dashboard'))
    page['title'] = 'View Posted job'
    
    reference_time = datetime.now()  # Current time as reference
    if request.method == 'POST':
        try:
            jobs = search_user_jobs(request.form.get("search-field"), request.form.get("some_input"), current_user.id)
        except:
            flash("Invalid search term")
            redirect(url_for("dashboard"))
    else:
        jobs = get_posted_job_byuser(current_user.id)
    return render_template("view_posted_job.html", page=page, jobs=jobs, reference_time=reference_time)

@login_required
@app.route('/view_job/<int:job_id>', methods = ['POST', 'GET'])
def view_job(job_id):
    page['title'] = 'Applications'
    if validate_user_view_job(job_id, current_user) != True:
        flash("You have no permit to view other's work")
        return redirect(url_for("dashboard"))

    if request.method == 'POST':
        try:
            applications = search_applications(job_id, request.form.get("search-field"), request.form.get("some_input"))
        except:
            flash("Invalid search term")
            redirect(url_for("dashboard"))
    else:
        applications = get_applications_by_job_id(job_id)
    reference_time = datetime.now()  # Current time as reference
    return render_template("view_job.html", page=page, applications=applications, job_id=job_id, reference_time=reference_time)

@login_required
@app.route('/view_application/<int:application_id>', methods = ['POST', 'GET'])
def view_application(application_id):

    
    page['title'] = 'View Application'
    return render_template('view_application.html', page=page, application_id=application_id)

@login_required
@app.route('/api/get_filename/<int:application_id>')
def get_filename(application_id):
    application = get_applications_by_application_id(application_id)
    return jsonify({"filename": application.resume_filename})

@login_required
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@login_required
@app.route('/view/<filename>')
def view_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)  # Ensure "uploads" is your file directory

@login_required
@app.route('/handle_application/<int:application_id>', methods=['POST'])
def handle_application(application_id):
    data = request.get_json()
    action = data.get('action')
    response_to_application(application_id, action)
    if action == 'approve':
        return jsonify({'status': "APPROVED"})
    elif action == 'reject':
        return jsonify({'status': "REJECTED"})
    else:
        return jsonify({"message": "Invalid action"}), 400    
@login_required
@app.route('/get_application_status/<int:application_id>', methods=['GET'])
def get_application_status(application_id):
    appli = get_applications_by_application_id(application_id)
    return jsonify({"status": Status(appli.status).name})
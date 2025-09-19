from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

from wtforms.validators import DataRequired, Length
from decimal import ROUND_HALF_UP
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    userrole = SelectField("Account Type", choices=[(2, 'User'), (3, 'Employer')],
                        coerce=int, validators=[DataRequired()]
    )
    submit = SubmitField("Register")

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField("Password", validators=[DataRequired()])
    new_password_repeat = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Change Password")

class JobPostForm(FlaskForm):
    title = StringField("Job Title", validators=[DataRequired(), Length(max=40)])
    company = StringField("Company", validators=[DataRequired(), Length(max=40)])
    description = StringField("Description", validators=[DataRequired(), Length(max=500)])
    location = StringField("Location", validators=[DataRequired(), Length(max=60)])
    salary = DecimalField(places=2, rounding=ROUND_HALF_UP, validators=[DataRequired()])
    submit = SubmitField("Post Job")

class JobApplyForm(FlaskForm):
    firstname = StringField("Firstname", validators=[DataRequired(), Length(max=40)])
    lastname = StringField("Lastname", validators=[DataRequired(), Length(max=40)])
    email = StringField("Email", validators=[DataRequired(), Length(max=40)])
    resume = FileField('Upload Resume', validators=[FileRequired()])
    submit = SubmitField("Submit Application")
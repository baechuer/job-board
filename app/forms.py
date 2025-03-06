from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    userrole = SelectField("Account Type", choices=[(2, 'User'), (3, 'Employer')],
                        coerce=int, validators=[DataRequired()]
    )
    submit = SubmitField("Register")

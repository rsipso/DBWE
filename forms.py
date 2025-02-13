# forms.py (Form Definitions)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateProjectForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Create Project')

class AddExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    user_id = SelectField('Paid By', coerce=int, validators=[DataRequired()])  # Will be populated dynamically
    submit = SubmitField('Add Expense')


class ShareProjectForm(FlaskForm):
    share_username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Share Project')
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, AnyOf

from .app import app

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(4, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class ProfileForm(FlaskForm):
    display_name = StringField('Display name', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField()


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 100)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(6, 150),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(6, 150)])
    # invite_code = StringField('Invite code', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField()


class ConfirmForm(FlaskForm):
    app.config['GROUP_INVITE_CODE']
    invite_code = StringField('Invite code', validators=[
        DataRequired(),
        Length(1, 100),
        AnyOf([app.config['GROUP_INVITE_CODE'], app.config['GROUP_INVITE_CODE'].lower()])
    ])

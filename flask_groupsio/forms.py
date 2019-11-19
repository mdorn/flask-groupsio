from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(4, 150)])
    remember = BooleanField('Remember me')
    submit = SubmitField()


class SubscribeForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 100)])
    # TODO: email validator

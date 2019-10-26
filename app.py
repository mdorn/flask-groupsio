# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
if app.config['ENV'] == 'production':  # reads from FLASK_ENV env variable
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')


# TODO: need to import after app.config takes place -- is this ok?
from . import views
from . import filters


app.secret_key = app.config['SECRET_KEY']


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', html=app.config['HOME_HTML'])

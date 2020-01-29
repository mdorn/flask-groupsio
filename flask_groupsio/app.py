# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, flash

from flask_talisman import Talisman
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length


app = Flask(__name__)


if app.config['ENV'] == 'production':  # reads from FLASK_ENV env variable
    app.config.from_object('flask_groupsio.config.ProductionConfig')
    Talisman(app, content_security_policy=None)
else:
    app.config.from_object('flask_groupsio.config.DevelopmentConfig')


# TODO: need to import after app.config takes place -- is this ok?
from flask_groupsio import views


app.secret_key = app.config['SECRET_KEY']


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


app.register_error_handler(404, page_not_found)
app.register_error_handler(500, server_error)
app.register_error_handler(401, unauthorized)

import json

import feedparser
import requests
import pytz

from dateutil.parser import parse

from flask import render_template, request, make_response, url_for, redirect, flash, session

from .app import app
from . import filters
from .forms import LoginForm
from .models import Message, File, Event, Member


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            params = {
                'email': form.username.data,
                'password': form.password.data,
            }
            req = requests.post('https://groups.io/api/v1/login', data=params)
            if req.status_code != 200:
                flash('Login failed.')
            else:
                resp = redirect(url_for('index'))
                cookies = dict(zip(req.cookies.keys(), req.cookies.values()))
                for key in cookies.keys():
                    resp.set_cookie(key, cookies[key])
                session['username'] = req.json()['user']['email']
                flash('Welcome {}!'.format(req.json()['user']['email']))
                return resp
        else:
            flash('Invalid form data.')
    resp = render_template('login.html', form=form)
    return resp


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    resp = redirect(url_for('index'))
    return resp


@app.route('/messages', methods=('GET',))
def messages():
    item = Message()
    data = item.all()
    return render_template(
        'messages.html',
        items=data
    )


@app.route('/files', methods=('GET',))
def files():
    item = File()
    data = item.all()
    return render_template('files.html', items=data)


@app.route('/calendar', methods=('GET',))
def calendar():
    item = Event()
    events = item.all()
    for_cal = []
    central = pytz.timezone('US/Central')
    for e in events:
        start = parse(e['start_time'])
        end = parse(e['end_time'])
        start_final = start.astimezone(central).isoformat()
        end_final = end.astimezone(central).isoformat()
        for_cal.append({
            'title': e['name'],
            'description': e['description'],
            'start': start_final,
            'end': end_final,
        })
    return render_template('calendar.html', items=for_cal)


@app.route('/feeds', methods=('GET',))
def feeds():
    feed = feedparser.parse(app.config['FEED_URL'])
    entries = feed['items']
    sorted_entries = sorted(entries, key=lambda entry: entry['published_parsed'])
    sorted_entries.reverse()
    return render_template(
        'feeds.html',
        items=sorted_entries[:50],
        feeds=app.config['FEEDS'],
        feed_url=app.config['FEED_URL']
    )


@app.route('/directory', methods=('GET',))
def directory():
    item = Member()
    data = item.all()
    return render_template('directory.html', items=data)

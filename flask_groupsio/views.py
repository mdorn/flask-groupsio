import json

import feedparser
import requests
import pytz

from dateutil.parser import parse

from flask import render_template, request, make_response, url_for, redirect, flash, session

from .app import app
from . import filters
from .forms import LoginForm, ProfileForm
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
                session['full_name'] = req.json()['user']['full_name']
                session['csrf'] = req.json()['user']['csrf_token']
                flash('Welcome {}!'.format(req.json()['user']['email']))
                if not session['full_name']:
                    flash(
                        'You have not yet set your display name. Please click on your email address in the upper right.',
                        'warning'
                    )
                return resp
        else:
            flash('Invalid form data.')
    resp = render_template('login.html', form=form)
    return resp


@app.route('/subscribe', methods=['GET'])
def subscribe():
    resp = render_template('subscribe.html')
    return resp


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm(display_name=session.get('full_name', ''))
    if request.method == 'POST':
        if form.validate():
            params = {
                'full_name': form.display_name.data,
                'csrf': session['csrf'],
            }
            req = requests.post('https://groups.io/api/v1/updateprofile', data=params, cookies=request.cookies)
            if req.status_code != 200:
                flash('Update failed.')
            else:
                resp = redirect(url_for('profile'))
                session['full_name'] = form.display_name.data
                flash('Profile updated!')
                return resp
        else:
            flash('Invalid form data.')
    resp = render_template('profile.html', form=form)
    return resp


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    resp = redirect(url_for('index'))
    return resp


@app.route('/messages', methods=('GET',))
def messages():
    # import pdb;pdb.set_trace()
    item = Message()
    data = item.all()
    return render_template(
        'messages.html',
        items=data
    )

@app.route('/files', methods=('GET',), defaults={'path': None})
@app.route('/files/<path>', methods=('GET',))
def files(path):
    item = File()
    if path:
        data = item.all_in_folder(path)
    else:
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
    # TODO: ensure this view can't be seen by the shared account
    item = Member()
    data = item.all()
    return render_template('directory.html', items=data)

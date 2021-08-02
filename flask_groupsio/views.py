import json

import requests
import pytz

from dateutil.parser import parse

from flask import render_template, request, url_for, redirect, flash, session
from werkzeug.exceptions import Unauthorized


from .app import app
from . import filters
from .forms import LoginForm, ProfileForm, SignupForm, ConfirmForm
from .models import Message, File, Event, Member
from .util import groupsio_admin_api_query, confirm_subscription
from .decorators import authorize

@app.route('/', methods=['GET', 'POST'])
def index():
    form = None
    if session.get('unconfirmed'):
        form = ConfirmForm()
    req = requests.get(app.config['HOME_CONTENT_URL'], timeout=2)
    items = json.loads(req.text)
    # print(items)
    return render_template(
        'index.html',
        html=app.config['HOME_HTML'],
        carousel_items=items,
        form=form
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username = ''
    if request.method == 'POST':
        if form.validate():
            params = {
                'email': form.username.data,
                'password': form.password.data,
            }
            req = requests.post('https://groups.io/api/v1/login', data=params)
            if req.status_code != 200:
                flash('Login failed.', 'danger')
            else:
                obj = req.json()
                resp = redirect(url_for('index'))
                if obj['user']['status'] != 'user_status_confirmed':
                    flash('Please check your inbox and confirm your Groups.io account before logging in.', 'warning')
                    return resp
                if not confirm_subscription(obj):
                    session['unconfirmed'] = True
                cookies = dict(zip(req.cookies.keys(), req.cookies.values()))
                for key in cookies.keys():
                    resp.set_cookie(key, cookies[key])
                session['username'] = obj['user']['email']
                session['full_name'] = obj['user']['full_name']
                session['csrf'] = obj['user']['csrf_token']
                flash('Welcome {}!'.format(obj['user']['email']))
                if not session['full_name']:
                    flash(
                        'You have not yet set your display name. Please click on your email address in the upper right.',
                        'warning'
                    )
                return resp
        else:
            flash('Invalid form data.', 'danger')
    else:
        username = request.args.get('email', '')
    resp = render_template('login.html', form=form, username=username)
    return resp


@app.route('/subscribe', methods=['GET'])
def subscribe():
    resp = render_template('subscribe.html')
    return resp


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate():
            data = {
                'email': form.email.data,
                'password': form.password.data,
            }
            result = groupsio_admin_api_query('https://groups.io/api/v1/registeruser', data=data)
            if 'user' in result:
                flash('Success! Please check your inbox for a confirmation email. After confirming your Groups.io account, you may login here.', 'success')
                return redirect(url_for('login', email=form.email.data))
            elif 'object' in result and result['object'] == 'error' and result['extra'] == 'email exists':
                flash('It appears you already have an account on Groups.io. Please login.', 'warning')
                return redirect(url_for('login', email=form.email.data))
        else:
            # import pdb;pdb.set_trace()
            messages = []
            for key in form.errors.keys():
                messages.append('<li>{}: {}</li>'.format(form[key].label.text, form.errors[key][0]))
            err_msg = '<p>There was a problem submitting your form:</p><ul>{}</ul>'.format(''.join(messages))
            flash(err_msg, 'danger')
    resp = render_template('signup.html', form=form)
    return resp


@app.route('/confirm', methods=['POST'])
def confirm():
    form = ConfirmForm()
    if form.validate():
        data = {
            'group_id': app.config['PARENT_GROUP_ID'],
            'subgroupids': app.config['GROUP_ID'],
            'emails': session['username'],
        }
        result = groupsio_admin_api_query('https://groups.io/api/v1/directadd', data=data)
        print(result)
        if 'object' in result and result['object'] == 'direct_add_results' and result['total_emails'] == 1:
            # NOTE: Groups.io will misreport an error if the user already belongs to parent group, so
            #   don't check for error
            # {'object': 'direct_add_results', 'total_emails': 1, 'errors': None, 'added_members': [
            session['unconfirmed'] = False
            flash('Success! You may now use the site. You will also receive a confirmation email that you have been added to the {} group on Groups.io.'.format(app.config['GROUP_NAME']))
        else:
            # TODO: logging/notification of errors
            flash('A problem occurred confirming your subscription.', 'danger')
    else:
        flash('Invalid invite code.', 'danger')
    return redirect(url_for('index'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    resp = redirect(url_for('index'))
    return resp


@app.route('/profile', methods=['GET', 'POST'])
@authorize
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
            flash('Invalid form data.', 'warning')
    resp = render_template('profile.html', form=form)
    return resp


@app.route('/messages', methods=('GET',))
@authorize
def messages():
    # import pdb;pdb.set_trace()
    item = Message()
    data = item.all()
    return render_template(
        'messages.html',
        items=data
    )

@app.route('/files', methods=('GET',), defaults={'path': None})
@app.route('/files/<path:path>', methods=('GET',))
@authorize
def files(path):
    item = File()
    if path:
        data = item.all_in_folder(path)
    else:
        # root level file listing
        data = item.all()
    return render_template('files.html', items=data)


@app.route('/get-file', methods=('GET',))
@authorize
def get_file():
    path = request.args.get('path')
    file = File()
    result = file.get_url(path)
    return redirect(result)


@app.route('/calendar', methods=('GET',))
@authorize
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
@authorize
def feeds():
    req = requests.get(app.config['FEED_URL'], timeout=2)
    items = json.loads(req.text)
    return render_template(
        'feeds.html',
        items=items,
        feeds=app.config['FEEDS'],
        feed_url=app.config['FEED_URL']
    )


@app.route('/directory', methods=('GET',))
@authorize
def directory():
    if session.get('username', None) == app.config['SHARED_ACCOUNT']:
        raise Unauthorized()
    if not session['full_name']:
        flash(
            'You have not yet set your display name. Please click on your email address in the upper right.',
            'warning'
        )
    item = Member()
    data = item.all()
    return render_template('directory.html', items=data)

import requests

from flask import request

from .app import app


def groupsio_api_query(url):
    req = requests.get(url, cookies=request.cookies)
    data = req.json()
    return data


def groupsio_admin_api_query(url, data):
    login_params = {
        'email': app.config['GROUP_ADMIN_USERNAME'],
        'password': app.config['GROUP_ADMIN_PASSWORD'],
    }
    req = requests.post('https://groups.io/api/v1/login', data=login_params)
    data['csrf'] = req.json()['user']['csrf_token']
    req2 = requests.post(url, data=data, cookies=req.cookies)
    results = req2.json()
    return results


def confirm_subscription(user_obj):
    if 'subscriptions' not in user_obj['user']:
        return False
    group_found = False
    for sub in user_obj['user']['subscriptions']:
        if sub['group_id'] == int(app.config['GROUP_ID']):
            group_found = True
            break
    return group_found

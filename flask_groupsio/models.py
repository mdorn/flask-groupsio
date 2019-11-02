from datetime import datetime, timedelta

from .app import app
from .util import groupsio_api_query

class Model(object):
    API_URL = ''

    def __init__(self):
        pass

    def get_api_url(self):
        return self.API_URL

    def all(self):
        resp = groupsio_api_query(self.get_api_url())
        if resp['data'] is not None:
            return resp['data']
        else:
            return []


class Message(Model):
    API_URL = 'https://groups.io/api/v1/gettopics?group_id={}'.format(app.config['GROUP_ID'])


class File(Model):
    API_URL = 'https://groups.io/api/v1/getfiledirectory?group_id={}'.format(app.config['GROUP_ID'])


class Event(Model):

    API_URL = 'https://groups.io/api/v1/getevents?group_id={}&start={}&end={}&limit=100'

    def get_api_url(self):
        today = datetime.today()
        start = timedelta(days=30)
        end = timedelta(days=365)
        first_date = (today - start).strftime('%Y-%m-%d')
        last_date = (today + end).strftime('%Y-%m-%d')
        url = self.API_URL.format(app.config['GROUP_ID'], first_date, last_date)
        return url


class Member(Model):
    API_URL = 'https://groups.io/api/v1/getmembers?group_id={}&limit=100'.format(app.config['GROUP_ID'])

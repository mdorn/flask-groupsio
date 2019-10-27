import json
import os

from dotenv import load_dotenv
load_dotenv()


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'foo'
    GROUP_ID = ''
    GROUP_NAME = ''
    GROUP_SHORT_NAME = ''
    GROUP_URL = 'https://group.groups.io/g/subgroup'

    HOME_HTML = '''
    <h1>Your Org</h1>
    <h2>Your Org Description</h2>
    <h3>Other</h3>
    '''

    FEED_URL = ''
    FEEDS = []


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY')
    GROUP_ID = os.getenv('GROUP_ID')
    GROUP_NAME = os.getenv('GROUP_NAME')
    GROUP_SHORT_NAME = os.getenv('GROUP_SHORT_NAME')
    GROUP_URL = os.getenv('GROUP_URL')
    HOME_HTML = os.getenv('HOME_HTML')
    FEED_URL = os.getenv('FEED_URL')
    FEEDS = json.loads(os.getenv('FEEDS'))
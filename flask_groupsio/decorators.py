from functools import wraps

from flask import session

from werkzeug.exceptions import Unauthorized


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('csrf') or session.get('unconfirmed'):
            raise Unauthorized()
        return f(*args, **kwargs)
    return decorated_function


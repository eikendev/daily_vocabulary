from functools import wraps

from .database import db_session


def session_function(f, *args, **kwargs):
    session = db_session()
    ret = f(*args, session=session, **kwargs)
    db_session.remove()
    return ret


def session_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return session_function(f, *args, **kwargs)

    return decorated_function

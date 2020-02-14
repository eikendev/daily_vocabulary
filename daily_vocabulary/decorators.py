from functools import wraps

from .database import db_session


def session_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session = db_session()
        f(*args, session, **kwargs)
        db_session.remove()

    return decorated_function

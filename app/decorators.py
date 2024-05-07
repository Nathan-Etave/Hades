from functools import wraps
from flask_login import current_user
from flask import abort


def admin_required(f):
    """
    Decorator that checks if the current user is an admin.
    If the user is not an admin, a 403 Forbidden error is raised.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function

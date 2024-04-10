from functools import wraps
from flask_login import current_user
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.id_Role == 1:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
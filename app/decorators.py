from functools import wraps
from flask_login import current_user, logout_user
from flask import abort, redirect, url_for


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

def active_required(f):
    """
    Decorator that checks if the current user is active.
    If the user is not active, disconnects the user and redirects to the login page.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.est_Actif_Utilisateur:
            logout_user()
            return redirect(url_for("login.login"))
        return f(*args, **kwargs)

    return decorated_function
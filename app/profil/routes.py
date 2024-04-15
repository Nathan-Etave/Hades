"""Routes for the profil blueprint."""
from flask import render_template, request
from flask_login import login_required, current_user
from app.profil import bp
from app.extensions import db
from app.decorators import admin_required

@bp.route('/', methods=['GET'])
@login_required
@admin_required
def profil():
    """Route to display the profile page.

    Returns:
        render_template: The profile page.
    """
    return render_template('profil/index.html', is_authenticated=True, is_admin=current_user.id_Role == 1, user=current_user)
from app.desktop import bp
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from app import socketio
from app.extensions import db
from app.models.fichier import FICHIER

@bp.route('/')
@login_required
def desktop():
    return render_template('desktop/index.html', is_authenticated=True, is_admin=current_user.id_Role == 1, has_notifications=current_user.NOTIFICATION != [])
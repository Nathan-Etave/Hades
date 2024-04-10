from app.notifications import bp
from app.models.notification import NOTIFICATION
from app.models.role import ROLE
from flask import render_template

@bp.route('/', methods=['GET'])
def notifications():
    notifications = NOTIFICATION.query.all()
    notifications = sorted(notifications, key=lambda x: x.datetime_Notification, reverse=True)
    roles = ROLE.query.all()
    return render_template('notifications/index.html', notifications=notifications, roles=roles, is_authenticated=True, is_admin=True)
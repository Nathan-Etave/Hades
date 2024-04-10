from app.notifications import bp
from app.extensions import db
from smtplib import SMTPException
from app.mail.mail import send_registration_confirmation_email, send_registration_rejection_email
from app.models.notification import NOTIFICATION
from app.models.utilisateur import UTILISATEUR
from app.models.role import ROLE
from flask import render_template, request
from flask_bcrypt import generate_password_hash
import secrets
import string

@bp.route('/', methods=['GET'])
def notifications():
    notifications = NOTIFICATION.query.all()
    notifications = sorted(notifications, key=lambda x: x.datetime_Notification, reverse=True)
    roles = ROLE.query.all()
    return render_template('notifications/index.html', notifications=notifications, roles=roles, is_authenticated=True, is_admin=True)

@bp.route('/<int:id_notification>/accept', methods=['GET', 'POST'])
def accept(id_notification):
    notification = NOTIFICATION.query.get(id_notification)
    if notification.type_Notification == 'Inscription':
        user = UTILISATEUR.query.get(notification.id_Utilisateur)
        user.id_Role = request.json.get('role_id')
        user.est_Actif_Utilisateur = True
        password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(10))
        user.mdp_Utilisateur = generate_password_hash(password)
        db.session.delete(notification)
        try:
            send_registration_confirmation_email(user.email_Utilisateur, password)
            db.session.commit()
        except (SMTPException, ConnectionError, TimeoutError):
            db.session.rollback()
            return "Erreur lors de l'envoi de l'email de confirmation", 200

    return render_template('notifications/index.html', is_authenticated=True, is_admin=True), 200
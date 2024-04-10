from app.notifications import bp
from app.extensions import db
from smtplib import SMTPException
from app.mail.mail import send_registration_confirmation_email, send_registration_rejection_email, send_reactivation_confirmation_email, send_reactivation_rejection_email
from app.decorators import admin_required
from app.models.notification import NOTIFICATION
from app.models.utilisateur import UTILISATEUR
from app.models.role import ROLE
from flask import render_template, request, flash, redirect, jsonify
from flask_bcrypt import generate_password_hash
from flask_login import login_required
import secrets
import string

@bp.route('/', methods=['GET'])
@login_required
@admin_required
def notifications():
    notifications = NOTIFICATION.query.all()
    notifications = sorted(notifications, key=lambda x: x.datetime_Notification, reverse=True)
    roles = ROLE.query.all()
    return render_template('notifications/index.html', notifications=notifications, roles=roles, is_authenticated=True, is_admin=True)

@bp.route('/<int:id_notification>/accept', methods=['GET', 'POST'])
@login_required
@admin_required
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
            return jsonify({'error': 'Erreur lors de l\'envoi du mail. Veuillez réessayer ultérieurement.'}), 500
    elif notification.type_Notification == 'Reactivation':
        user = UTILISATEUR.query.get(notification.id_Utilisateur)
        user.id_Role = request.json.get('role_id')
        user.est_Actif_Utilisateur = True
        db.session.delete(notification)
        try:
            send_reactivation_confirmation_email(user.email_Utilisateur)
            db.session.commit()
        except (SMTPException, ConnectionError, TimeoutError):
            db.session.rollback()
            return jsonify({'error': 'Erreur lors de l\'envoi du mail. Veuillez réessayer ultérieurement.'}), 500
    return render_template('notifications/index.html', is_authenticated=True, is_admin=True), 200

@bp.route('/<int:id_notification>/reject', methods=['GET', 'POST'])
@login_required
@admin_required
def reject(id_notification):
    notification = NOTIFICATION.query.get(id_notification)
    if notification.type_Notification == 'Inscription':
        user = UTILISATEUR.query.get(notification.id_Utilisateur)
        db.session.delete(notification)
        try:
            send_registration_rejection_email(user.email_Utilisateur)
            db.session.delete(user)
            db.session.commit()
        except (SMTPException, ConnectionError, TimeoutError):
            db.session.rollback()
            return jsonify({'error': 'Erreur lors de l\'envoi du mail. Veuillez réessayer ultérieurement.'}), 500
    elif notification.type_Notification == 'Reactivation':
        user = UTILISATEUR.query.get(notification.id_Utilisateur)
        db.session.delete(notification)
        try:
            send_reactivation_rejection_email(user.email_Utilisateur)
            db.session.commit()
        except (SMTPException, ConnectionError, TimeoutError):
            db.session.rollback()
            return jsonify({'error': 'Erreur lors de l\'envoi du mail. Veuillez réessayer ultérieurement.'}), 500
    return render_template('notifications/index.html', is_authenticated=True, is_admin=True), 200
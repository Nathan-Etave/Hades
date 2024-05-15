"""Routes for the notifications blueprint."""

import secrets
import string
import json
from smtplib import SMTPException
from flask import render_template, request, jsonify
from flask_bcrypt import generate_password_hash
from flask_login import login_required, current_user
from app.notifications import bp
from app.mail import (
    send_registration_confirmation_email,
    send_registration_rejection_email,
    send_reactivation_confirmation_email,
    send_reactivation_rejection_email,
)
from app.decorators import admin_required, active_required
from app.models.notification import NOTIFICATION
from app.models.utilisateur import UTILISATEUR
from app.models.role import ROLE
from app.utils import check_notitications
from app.extensions import redis, socketio, db
from datetime import datetime

@socketio.on('connect', namespace='/notifications')

@bp.route("/", methods=["GET"])
@login_required
@active_required
def notifications():
    """Route for the notifications page."""
    all_notifications = NOTIFICATION.query.all()
    all_notifications = sorted(
        all_notifications, key=lambda x: x.datetime_Notification, reverse=True
    )
    roles = ROLE.query.all()
    processed_files = redis.lrange('processed_files', 0, -1)
    processed_files = [json.loads(file) for file in processed_files if file is not None]
    processed_files.sort(key=lambda file: file['file']['date_Fichier'], reverse=True)
    for file in processed_files:
        date_str = file['file']['date_Fichier'].split(':')[0] + ':' + file['file']['date_Fichier'].split(':')[1]
        file['file']['date_Fichier'] = datetime.strptime(date_str, '%d/%m/%Y %H:%M').strftime('%d/%m/%Y %H:%M')
        file['folder']['nom_Dossier'] = file['folder']['nom_Dossier']
    return render_template(
        "notifications/index.html",
        notifications=all_notifications,
        roles=roles,
        is_authenticated=True,
        is_admin=current_user.is_admin(),
        display_notification=current_user.id_Role == 1,
        processed_files = processed_files,
        has_notifications=check_notitications(),
        title="Notifications",
    )


def handle_acceptance(notification, send_email_function, success_message):
    """Function to handle the acceptance of a notification.

    Args:
        notification (NOTIFICATION): The notification to handle.
        send_email_function (function): The function to send the email.
        success_message (str): The success message to display.

    Returns:
        JSON: The JSON response.
    """
    user = UTILISATEUR.query.get(notification.id_Utilisateur)
    user.id_Role = request.json.get("role_id")
    user.est_Actif_Utilisateur = 1
    db.session.delete(notification)
    try:
        send_email_function(user.email_Utilisateur)
        db.session.commit()
    except (SMTPException, ConnectionError, TimeoutError):
        db.session.rollback()
        return jsonify(
            {
                "error": f"{user.email_Utilisateur} : Erreur lors de l'envoi du mail. Veuillez réessayer ultérieurement."
            }
        ), 500
    return jsonify({"message": f"{user.email_Utilisateur} : {success_message}"}), 200


def handle_rejection(notification, send_email_function, success_message):
    """Function to handle the rejection of a notification.

    Args:
        notification (NOTIFICATION): The notification to handle.
        send_email_function (function): The function to send the email.
        success_message (str): The success message to display.

    Returns:
        JSON: The JSON response.
    """
    user = UTILISATEUR.query.get(notification.id_Utilisateur)
    db.session.delete(notification)
    try:
        send_email_function(user.email_Utilisateur)
        if str(notification.type_Notification) == "1":
            db.session.delete(user)
        db.session.commit()
    except (SMTPException, ConnectionError, TimeoutError):
        db.session.rollback()
        return jsonify(
            {
                "error": f"{user.email_Utilisateur} : Erreur lors de l'envoi du mail. Veuillez réessayer ultérieurement."
            }
        ), 500
    return jsonify({"message": f"{user.email_Utilisateur} : {success_message}"}), 200


@bp.route("/<int:id_notification>/accept", methods=["GET", "POST"])
@login_required
@active_required
@admin_required
def accept(id_notification):
    """Route to accept a notification.

    Args:
        id_notification (int): The id of the notification to accept.

    Returns:
        JSON: The JSON response.
    """
    if current_user.id_Role != 1:
        return jsonify({"error": "Vous n'avez pas les droits pour effectuer cette action."}), 403
    notification = NOTIFICATION.query.get(id_notification)
    if str(notification.type_Notification) == "1":
        return handle_acceptance(
            notification, send_registration_confirmation_email, "Inscription validée."
        )
    elif str(notification.type_Notification) == "2":
        return handle_acceptance(
            notification, send_reactivation_confirmation_email, "Réactivation validée."
        )


@bp.route("/<int:id_notification>/reject", methods=["GET", "POST"])
@login_required
@active_required
@admin_required
def reject(id_notification):
    """Route to reject a notification.

    Args:
        id_notification (int): The id of the notification to reject.

    Returns:
        JSON: The JSON response.
    """
    if current_user.id_Role != 1:
        return jsonify({"error": "Vous n'avez pas les droits pour effectuer cette action."}), 403
    notification = NOTIFICATION.query.get(id_notification)
    if str(notification.type_Notification) == "1":
        return handle_rejection(
            notification, send_registration_rejection_email, "Inscription refusée."
        )
    elif str(notification.type_Notification) == "2":
        return handle_rejection(
            notification, send_reactivation_rejection_email, "Réactivation refusée."
        )

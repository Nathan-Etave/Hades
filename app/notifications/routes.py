"""Routes for the notifications blueprint."""

import secrets
import string
from smtplib import SMTPException
from flask import render_template, request, jsonify
from flask_bcrypt import generate_password_hash
from flask_login import login_required, current_user
from app.notifications import bp
from app.extensions import db
from app.mail.mail import (
    send_registration_confirmation_email,
    send_registration_rejection_email,
    send_reactivation_confirmation_email,
    send_reactivation_rejection_email,
)
from app.decorators import admin_required
from app.models.notification import NOTIFICATION
from app.models.utilisateur import UTILISATEUR
from app.models.role import ROLE


@bp.route("/", methods=["GET"])
@login_required
@admin_required
def notifications():
    """Route for the notifications page."""
    all_notifications = NOTIFICATION.query.all()
    all_notifications = sorted(
        all_notifications, key=lambda x: x.datetime_Notification, reverse=True
    )
    roles = ROLE.query.all()
    return render_template(
        "notifications/index.html",
        notifications=all_notifications,
        roles=roles,
        is_authenticated=True,
        is_admin=True,
        has_notifications=current_user.NOTIFICATION != [],
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
    user.est_Actif_Utilisateur = True
    if notification.type_Notification == "Inscription":
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for i in range(10)
        )
        user.mdp_Utilisateur = generate_password_hash(password)
    db.session.delete(notification)
    try:
        if notification.type_Notification == "Inscription":
            send_email_function(user.email_Utilisateur, password)
        else:
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
        if notification.type_Notification == "Inscription":
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
@admin_required
def accept(id_notification):
    """Route to accept a notification.

    Args:
        id_notification (int): The id of the notification to accept.

    Returns:
        JSON: The JSON response.
    """
    notification = NOTIFICATION.query.get(id_notification)
    if notification.type_Notification == "Inscription":
        return handle_acceptance(
            notification, send_registration_confirmation_email, "Inscription validée."
        )
    elif notification.type_Notification == "Reactivation":
        return handle_acceptance(
            notification, send_reactivation_confirmation_email, "Réactivation validée."
        )


@bp.route("/<int:id_notification>/reject", methods=["GET", "POST"])
@login_required
@admin_required
def reject(id_notification):
    """Route to reject a notification.

    Args:
        id_notification (int): The id of the notification to reject.

    Returns:
        JSON: The JSON response.
    """
    notification = NOTIFICATION.query.get(id_notification)
    if notification.type_Notification == "Inscription":
        return handle_rejection(
            notification, send_registration_rejection_email, "Inscription refusée."
        )
    elif notification.type_Notification == "Reactivation":
        return handle_rejection(
            notification, send_reactivation_rejection_email, "Réactivation refusée."
        )

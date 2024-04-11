"""
Module for handling login routes.
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_user
from flask_bcrypt import check_password_hash, generate_password_hash
from app.login import bp
from app.models.utilisateur import UTILISATEUR
from app.models.notification import NOTIFICATION
from app.forms.login_form import LoginForm
from app.forms.forgotten_password_form import ForgottenPasswordForm
from app import login_manager
from app.extensions import db
from datetime import datetime
from flask import jsonify, request
import secrets
import string
from app.mail.mail import send_forgotten_password_email


@login_manager.user_loader
def load_user(user):
    return UTILISATEUR.query.get(user)


@bp.route("/", methods=["GET", "POST"])
def login():
    """
    Handles the login functionality.

    This function validates the login form and performs the necessary actions based on the form data.
    If the form is valid, it checks if the user exists and if the password is correct.
    If the user is inactive, appropriate flash messages are displayed.
    If the password is incorrect, a flash message is displayed.
    If the user does not exist, a flash message is displayed.
    If the forgotten password form is submitted, it sends a email with new pasword to the user's email address.

    Returns:
        The rendered login template with the login form and forgotten password form.
    """
    form = LoginForm()
    mdp_form = ForgottenPasswordForm()
    if form.validate_on_submit():
        user = UTILISATEUR.query.filter_by(email_Utilisateur=form.email.data).first()
        if user:
            if user.est_Actif_Utilisateur != 1:
                if user.id_Role:
                    flash("Votre compte est désactivé.", "info")
                else:
                    flash("Votre compte n'est pas encore activé.", "danger")
                form.email.data = form.email.data
                return render_template("login/index.html", form=form, mdp_form=mdp_form)
            if check_password_hash(user.mdp_Utilisateur, form.password.data):
                login_user(user)
                return redirect(url_for("home.home"))
            flash("Mot de passe incorrect.", "danger")
            form.email.data = form.email.data
            return render_template("login/index.html", form=form, mdp_form=mdp_form)
        flash("Adresse email inconnu.", "danger")
        form.email.data = form.email.data
        return render_template("login/index.html", form=form, mdp_form=mdp_form)
    if mdp_form.validate_on_submit():
        user = UTILISATEUR.query.filter_by(
            email_Utilisateur=mdp_form.email.data
        ).first()
        if user:
            if user.est_Actif_Utilisateur != 1:
                if user.id_Role:
                    flash("Votre compte est désactivé.", "info")
                else:
                    flash("Votre compte n'est pas encore activé.", "danger")
            else:
                response = forgot_password(user.email_Utilisateur)
                flash(response[0], response[1])
        else:
            flash("Adresse email inconnu.", "danger")
    return render_template("login/index.html", form=form, mdp_form=mdp_form)


@bp.route("/notification", methods=["POST"])
def add_notification():
    """
    Add a notification for a user.

    Returns:
        JSON: The created notification in JSON format.
    """
    current_date = datetime.now()
    type = request.json.get("type")
    email_user = request.json.get("email_user")
    id_user = (
        UTILISATEUR.query.filter_by(email_Utilisateur=email_user).first().id_Utilisateur
    )
    if id_user is None:
        return jsonify({"error": "user not found"}), 404
    notification = NOTIFICATION.query.filter_by(id_Utilisateur=id_user).first()
    if notification:
        return jsonify({"error": "user already have a notification"}), 404
    notification = NOTIFICATION(
        datetime_Notification=current_date,
        type_Notification=type,
        id_Utilisateur=id_user,
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify(notification.to_dict()), 200


def forgot_password(email):
    """
    Sends a forgotten password email to the user and updates their password in the database.

    Args:
        email (str): The email address of the user.

    Returns:
        list: A list containing a message and a status indicating the result of the operation.
    """
    user = UTILISATEUR.query.filter_by(email_Utilisateur=email).first()
    password = "".join(
        secrets.choice(string.ascii_letters + string.digits + string.punctuation)
        for i in range(10)
    )
    user.mdp_Utilisateur = generate_password_hash(password)
    try:
        send_forgotten_password_email(user.email_Utilisateur, password)
        db.session.commit()
    except OSError:
        db.session.rollback()
        return ["Erreur lors de l'envoie du mail de confirmation", "danger"]
    return ["Un email vous a été envoyé avec votre nouveau mot de passe.", "success"]

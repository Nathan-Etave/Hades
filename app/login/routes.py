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
from smtplib import SMTPException


@login_manager.user_loader
def load_user(user):
    return UTILISATEUR.query.get(user)


@bp.route("/", methods=["GET", "POST"])
def login():
    """
    Login route handler.
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
            if check_password_hash(user.mdp_Utilisateur, form.password.data):
                login_user(user)
                return redirect(url_for("home.index"))
            flash("Mot de passe incorrect.", "danger")
            form.email.data = form.email.data
        flash("Adresse email inconnu.", "danger")
        form.email.data = form.email.data
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

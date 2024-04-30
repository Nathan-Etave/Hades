"""Routes for the registration page."""

from datetime import datetime
from smtplib import SMTPException
from flask import render_template, redirect, url_for, flash
from app.register import bp
from app.extensions import db
from app.mail.mail import send_registration_request_email
from app.forms.registration_form import RegistrationForm
from app.models.utilisateur import UTILISATEUR
from app.models.notification import NOTIFICATION
from flask_login import current_user

@bp.route("/", methods=["GET", "POST"])
def register() -> any:
    """Route to register a new user.

    Returns:
        any: Redirect to the registration page.
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for("home.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = UTILISATEUR.query.filter_by(email_Utilisateur=form.email.data).first()
        if user and user.est_Actif_Utilisateur:
            flash("Un compte existe déjà avec cet email.", "danger")
        elif user and not user.est_Actif_Utilisateur and user.id_Role is not None:
            flash("Un compte désactivé existe déjà avec cet email.", "danger")
        elif user and not user.est_Actif_Utilisateur and user.id_Role is None:
            flash(
                "Un compte en attente d'activation existe déjà avec cet email.",
                "danger",
            )
        else:
            user = UTILISATEUR(
                nom_Utilisateur=form.last_name.data,
                prenom_Utilisateur=form.first_name.data,
                email_Utilisateur=form.email.data,
                est_Actif_Utilisateur=False,
            )
            db.session.add(user)
            db.session.commit()
            notification = NOTIFICATION(
                datetime_Notification=datetime.now(),
                type_Notification=1,
                id_Utilisateur=user.id_Utilisateur,
            )
            db.session.add(notification)
            db.session.commit()
            try:
                send_registration_request_email(user.email_Utilisateur)
                flash("Demande d'inscription envoyée avec succès.", "success")
            except (SMTPException, ConnectionError, TimeoutError):
                flash(
                    "Erreur lors de l'envoi de l'email. Votre demande d'inscription est cependant enregistrée.",
                    "warning",
                )
        return redirect(url_for("register.register"))
    return render_template("register/index.html", form=form, is_authenticated=False)

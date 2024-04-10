"""
Module for handling login routes.
"""

from flask import render_template, redirect, url_for, flash
from flask_login import login_user
from flask_bcrypt import check_password_hash
from app.login import bp
from app.models.utilisateur import UTILISATEUR
from app.forms.login_form import LoginForm


@bp.route("/", methods=["GET", "POST"])
def login():
    """
    Login route handler.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = UTILISATEUR.query.filter_by(email_Utilisateur=form.email.data).first()
        if user:
            if user.est_Actif_Utilisateur != 1:
                if user.id_Role:
                    flash("Votre compte est désactivé", "danger")
                else:
                    flash("Votre compte n'est pas encore activé", "danger")
                return redirect(url_for("login.login"))
            if check_password_hash(user.mdp_Utilisateur, form.password.data):
                login_user(user)
                flash("Connexion réussie", "success")
                return redirect(url_for("home.index"))
            flash("Mot de passe incorrect", "danger")
            return redirect(url_for("login.login"))
        flash("Adresse email inconnu", "danger")
        return redirect(url_for("login.login"))
    return render_template("login/index.html", form=form)

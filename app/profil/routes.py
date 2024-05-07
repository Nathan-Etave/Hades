"""Routes for the profil blueprint."""

from flask import render_template, request, jsonify, url_for, redirect, abort
from flask_login import login_required, current_user, logout_user
from app.profil import bp
from app.extensions import db
from app.forms.edit_profil_form import Edit_profil_form
from flask_bcrypt import check_password_hash, generate_password_hash
from app.models.utilisateur import UTILISATEUR
from app.utils import check_notitications
from app.models.role import ROLE


@bp.route("/", methods=["GET", "POST"])
@login_required
def profil():
    """Route to display the profile page.

    Returns:
        render_template: The profile page.
    """
    return render_template(
        "profil/index.html",
        is_authenticated=True,
        is_admin=current_user.is_admin(),
        has_notifications=check_notitications(),
        user=current_user,
        user_role=db.session.query(ROLE.nom_Role)
        .filter(ROLE.id_Role == current_user.id_Role)
        .first()[0],
        edit_mode=False,
    )


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """
    Edit the user profile.

    Returns:
        If the form is valid, redirects to the user's profile page.
        Otherwise, renders the profile edit page with the form and user data.
    """
    if not request.referrer or "profil" not in request.referrer:
        return redirect(url_for("profil.profil"))

    form = Edit_profil_form()
    if form.validate_on_submit():
        edit_user(
            current_user.id_Utilisateur,
            form.last_name.data,
            form.first_name.data,
            form.email.data,
            form.telephone.data,
            form.password.data,
        )
        return redirect(url_for("profil.profil"))
    else:
        form.last_name.data = current_user.nom_Utilisateur
        form.first_name.data = current_user.prenom_Utilisateur
        form.email.data = current_user.email_Utilisateur
        form.telephone.data = current_user.telephone_Utilisateur
    return render_template(
        "profil/index.html",
        is_authenticated=True,
        is_admin=current_user.is_admin(),
        has_notifications=check_notitications(),
        user=current_user,
        form=form,
        edit_mode=True,
    )


@bp.route("/verification", methods=["POST"])
@login_required
def verification():
    """
    Verify the password provided by the user.

    Returns:
        A JSON response containing the result of the password verification.
    """
    password = request.json.get("password")
    return jsonify(
        {"verif": check_password_hash(current_user.mdp_Utilisateur, password)}
    )


@bp.route("/deconnexion", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"status": "success"})


def edit_user(id, last_name, first_name, email, telephone, password):
    """Edit the user in the database.

    Args:
        id (int): The user's id.
        last_name (str): The user's last name.
        first_name (str): The user's first name.
        email (str): The user's email.
        password (str): The user's password.
    """
    user = UTILISATEUR.query.get(id)
    user.nom_Utilisateur = last_name
    user.prenom_Utilisateur = first_name
    user.email_Utilisateur = email
    user.telephone_Utilisateur = telephone
    user.mdp_Utilisateur = generate_password_hash(password)
    db.session.commit()

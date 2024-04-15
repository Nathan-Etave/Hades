"""Routes for the profil blueprint."""
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.profil import bp
from app.extensions import db
from app.forms.edit_profil_form import Edit_profil_form
from flask_bcrypt import check_password_hash

@bp.route('/', methods=['GET', 'POST'])
@login_required
def profil():
    """Route to display the profile page.

    Returns:
        render_template: The profile page.
    """
    form = Edit_profil_form()
    return render_template('profil/index.html', is_authenticated=True, is_admin=current_user.id_Role == 1, user=current_user, form=form)

@bp.route('/verification', methods=['POST'])
@login_required
def verification() :
    password = request.json.get("password")
    return jsonify({'verif' : check_password_hash(current_user.mdp_Utilisateur, password)})

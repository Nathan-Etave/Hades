from app.home import bp
from flask_login import login_required, current_user
from flask import render_template, request, jsonify, redirect, url_for
from app.extensions import db
from app.models.favoris import FAVORIS
from app.models.fichier import FICHIER
from app.models.a_recherche import A_RECHERCHE
from app.forms.search_form import SearchForm
from datetime import datetime
from app.utils import Whoosh

@bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    favorite_files = get_files_favoris(current_user.id_Utilisateur)
    researches = get_user_researches(current_user.id_Utilisateur)
    form = SearchForm()
    if form.validate_on_submit():
        add_research(current_user.id_Utilisateur, form.search.data)
        return redirect(url_for('search.search', query=form.search.data))
    return render_template("home/index.html", is_authenticated=True, is_admin=current_user.id_Role == 1, favorite_files=favorite_files, researches=researches, form=form)

@bp.route('/favori/<int:id_file>', methods=['DELETE'])
@login_required
def unfavorize(id_file):
    unfavorite_file(id_file, current_user.get_id())
    return jsonify({'status': 'ok'})


def get_files_favoris(user_id):
    """
    Retrieve the files favorited by a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of files favorited by the user.
    """
    files = db.session.query(FICHIER).join(FAVORIS).filter(FAVORIS.c.id_Utilisateur == user_id).all()
    return files

def get_user_researches(user_id):
    """
    Retrieve the researches made by a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of researches made by the user.
    """
    researches = db.session.query(A_RECHERCHE).filter(A_RECHERCHE.id_Utilisateur == user_id).order_by(A_RECHERCHE.datetime_Recherche.desc()).limit(8).all()
    return researches

def add_research(user_id, search):
    """
    Add a research to the database.

    Args:
        user_id (int): The ID of the user.
        search (str): The search query.
    """
    research = A_RECHERCHE(id_Utilisateur=user_id, champ_Recherche=search, datetime_Recherche=datetime.now())
    db.session.add(research)
    db.session.commit()

def unfavorite_file(file_id, user_id):
    """
    Remove a file from the favorites of a user.

    Args:
        file_id (int): The ID of the file.
        user_id (int): The ID of the user.
    """
    print(file_id, user_id)
    db.session.query(FAVORIS).filter(FAVORIS.c.id_Fichier == file_id, FAVORIS.c.id_Utilisateur == user_id).delete()
    db.session.commit()

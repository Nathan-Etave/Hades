from app.search import bp
from flask_login import login_required, current_user
from flask import render_template, request, jsonify, current_app
from app.extensions import db
from app.models.dossier import DOSSIER
from app.models.favoris import FAVORIS
from app.utils import Whoosh
from app.forms.search_form import SearchForm
from app import socketio
from fasteners import InterProcessLock
from app.utils import check_notitications


@bp.route("/", methods=["GET", "POST"])
@login_required
def search():
    """
    Perform a search based on the query parameter and return the search results.

    Returns:
        A rendered template with the search results, query, and search form.
    """
    query = request.args.get("query")
    whoosh = Whoosh()
    results = whoosh.search(query)
    results = create_rendered_list(results)
    form = SearchForm()
    return render_template(
        "search/index.html",
        is_authenticated=True,
        is_admin=current_user.is_admin(),
        has_notifications=check_notitications(),
        folders=results,
        query=query,
        form=form,
    )


@bp.route("/favori/<int:id_file>", methods=["POST", "DELETE"])
@login_required
def favorize(id_file):
    """
    Favorize or unfavorize a file for the current user.

    Args:
        id_file (int): The ID of the file to favorize or unfavorize.

    Returns:
        dict: A JSON response indicating the status of the operation.
            The response will have a 'status' key with the value 'ok'.
    """
    if request.method == "POST":
        db.session.execute(
            FAVORIS.insert().values(
                id_Fichier=id_file, id_Utilisateur=current_user.id_Utilisateur
            )
        )
    else:
        db.session.query(FAVORIS).filter(
            FAVORIS.c.id_Fichier == id_file,
            FAVORIS.c.id_Utilisateur == current_user.id_Utilisateur,
        ).delete()
    db.session.commit()
    return jsonify({"status": "ok"})


def create_folder_dict(folder, files):
    """
    Create a dictionary representation of a folder.

    Args:
        folder (Folder): The folder object.
        files (list): A list of file objects.

    Returns:
        dict: A dictionary representation of the folder, including its name, files, color, id, and subfolders.
    """
    files_in_folder = [
        result for result in files if result["path"] == (str(folder.id_Dossier))
    ]
    subfolders = recursive_subfolder(folder, files)
    return {
        "name": folder.nom_Dossier,
        "files": files_in_folder,
        "color": folder.couleur_Dossier,
        "id": folder.id_Dossier,
        "subfolder": subfolders
    }

def create_rendered_list(results):
    """
    Create a rendered list of folders and their associated results.

    Args:
        results (list): A list of results.

    Returns:
        list: A list of dictionaries representing folders and their associated results.
    """
    folders = db.session.query(DOSSIER).order_by(DOSSIER.priorite_Dossier).all()
    folders_root = [folder for folder in folders if folder.DOSSIER == [] and is_accessible(folder)]
    return [create_folder_dict(folder, results) for folder in folders_root]


def recursive_subfolder(folder, files):
    """
    Recursively searches for subfolders in the given folder and creates a list of dictionaries
    containing information about each subfolder.

    Args:
        folder (str): The path of the folder to search for subfolders.
        files (list): A list of files to include in the dictionaries.

    Returns:
        list: A list of dictionaries containing information about each subfolder.
    """
    return [create_folder_dict(subfolder, files) for subfolder in folder.DOSSIER_ if is_accessible(subfolder)]

def is_accessible(folder):
    """
    Check if the current user has access to the given folder.

    Args:
        folder (Folder): The folder to check.

    Returns:
        bool: True if the user has access to the folder, False otherwise.
    """
    return any(current_user.id_Role == role.id_Role for role in folder.ROLE)

@socketio.on('search_files', namespace='/search')
def search_files(data):
    search_query = data.get('query')
    with InterProcessLock(f'{current_app.root_path}/whoosh.lock'):
        search_results = Whoosh().search(search_query)
    search_results = create_rendered_list(search_results)
    socketio.emit('search_results', search_results, namespace='/search')

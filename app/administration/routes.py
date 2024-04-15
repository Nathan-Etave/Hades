import os
from base64 import b64decode
from app.administration import bp
from flask import render_template, request, current_app, Response, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required
from app.decorators import admin_required
from app.extensions import db
from app.models.dossier import DOSSIER
from app.models.fichier import FICHIER
from app.utils import Whoosh, NLPProcessor, FileReader

@bp.route("/")
@login_required
@admin_required
def administration():
    all_folders = DOSSIER.query.all()
    all_root_folders = [folder for folder in all_folders if folder.DOSSIER == []]
    return render_template("administration/index.html", folders=all_root_folders, is_admin=True, is_authenticated=True)

@bp.route("/upload", methods=["POST"])
@login_required
@admin_required
def upload():
    json = request.get_json()
    folder_id = json.get("folderId")
    file_data = json.get("data")
    filename = secure_filename(json.get("filename"))
    storage_directory = os.path.join(current_app.root_path, "storage")
    if not os.path.exists(f"{storage_directory}/{folder_id}"):
        os.makedirs(f"{storage_directory}/{folder_id}")
    file = FICHIER(id_Dossier=folder_id, nom_Fichier=filename, extension_Fichier=filename.split(".")[-1])
    db.session.add(file)
    db.session.commit()
    file_path = os.path.join(storage_directory, folder_id, f'{file.id_Fichier}.{file.extension_Fichier}')
    with open(file_path, "wb") as new_file:
        new_file.write(b64decode(file_data.split(",")[1]))
        print(file_path)
    print(FileReader().read(file_path, file.extension_Fichier))
    return Response(status=200)
import os
from base64 import b64decode
from app.administration import bp
from app import socketio, rq
from unidecode import unidecode
from flask import render_template, request, current_app, Response
from flask_socketio import emit
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
    filename = unidecode(secure_filename(json.get("filename"))).lower()
    storage_directory = os.path.join(current_app.root_path, "storage")
    if not os.path.exists(f"{storage_directory}/{folder_id}"):
        os.makedirs(f"{storage_directory}/{folder_id}")
    file = FICHIER(id_Dossier=folder_id, nom_Fichier=filename, extension_Fichier=filename.split(".")[-1])
    db.session.add(file)
    db.session.commit()
    file_path = os.path.join(storage_directory, folder_id, f'{file.id_Fichier}.{file.extension_Fichier}')
    with open(file_path, "wb") as new_file:
        new_file.write(b64decode(file_data.split(",")[1]))
    rq.enqueue(process_file, file_path, filename, folder_id, file.id_Fichier)
    add_file_to_queue(filename)
    return Response(status=200)

def process_file(file_path, filename, folder_id, file_id):
    file_text = FileReader().read(file_path, filename.split(".")[-1])
    file_tags = ' '.join(NLPProcessor().tokenize(file_text))
    Whoosh().add_document(filename, file_text, folder_id, file_tags, file_id)
    remove_file_from_queue()
    rq.connection.incr("total_files_processed")
    rq.connection.publish("progress", {
        'current_file': filename,
        'next_file': get_next_file(),
        'total_files': get_total_files(),
        'total_file_processed': get_total_files_processed()
    })

def add_file_to_queue(filename):
    rq.connection.rpush("files_queue", filename)

def remove_file_from_queue():
    rq.connection.lpop("files_queue")

def get_next_file():
    return rq.connection.lindex("files_queue", 0)

def get_total_files():
    return rq.connection.llen("files_queue")

def get_total_files_processed():
    return rq.connection.get("total_files_processed")

@socketio.on("connect")
def on_connect():
    pubsub = rq.connection.pubsub()
    pubsub.subscribe("progress")
    for message in pubsub.listen():
        if message["type"] == "message":
            emit("progress", message["data"])

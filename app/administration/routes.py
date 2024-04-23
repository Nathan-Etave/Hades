import os
import json
from base64 import b64decode
from app import redis, socketio
from app.administration import bp
from app.tasks import process_file
from unidecode import unidecode
from flask import render_template, request, current_app, Response
from werkzeug.utils import secure_filename
from flask_login import login_required
from app.decorators import admin_required
from app.extensions import db
from app.models.dossier import DOSSIER
from app.models.fichier import FICHIER
from app.models.utilisateur import UTILISATEUR
from app.models.role import ROLE
from app.utils import Whoosh
from fasteners import InterProcessLock


@bp.route("/")
@login_required
@admin_required
def administration():
    all_folders = DOSSIER.query.all()
    all_root_folders = [folder for folder in all_folders if folder.DOSSIER == []]
    all_root_folders.sort(key=lambda x: x.priorite_Dossier)
    all_users = UTILISATEUR.query.all()
    all_users = [user for user in all_users if user.id_Role is not None]
    all_roles = ROLE.query.all()
    return render_template(
        "administration/index.html",
        folders=all_root_folders,
        users=all_users,
        roles=all_roles,
        is_admin=True,
        is_authenticated=True,
    )


@bp.route("/upload", methods=["POST"])
@login_required
@admin_required
def upload():
    if redis.get("total_files") == redis.get("total_files_processed"):
        redis.set("total_files", 0)
        redis.set("total_files_processed", 0)
    json_data = request.get_json()
    folder_id = json_data.get("folderId")
    file_data = json_data.get("data")
    filename = unidecode(secure_filename(json_data.get("filename"))).lower()
    storage_directory = os.path.join(current_app.root_path, "storage")
    if not os.path.exists(f"{storage_directory}/{folder_id}"):
        os.makedirs(f"{storage_directory}/{folder_id}")
    file = FICHIER(
        id_Dossier=folder_id,
        nom_Fichier=filename,
        extension_Fichier=filename.split(".")[-1],
    )
    db.session.add(file)
    db.session.commit()
    file_path = os.path.join(
        storage_directory, folder_id, f"{file.id_Fichier}.{file.extension_Fichier}"
    )
    with open(file_path, "wb") as new_file:
        new_file.write(b64decode(file_data.split(",")[1]))
    process_file.apply_async(args=[file_path, filename, folder_id, str(file.id_Fichier)])
    redis.incr("total_files")
    redis.rpush(
        "file_queue", json.dumps({"file_id": file.id_Fichier, "filename": filename})
    )
    return Response(status=200)


@socketio.on("connect", namespace="/administration")
def connect():
    workers = redis.keys("worker:*") if len(redis.keys("worker:*")) > 0 else []
    for worker in workers:
        socketio.emit(
            "worker_status",
            json.loads(redis.get(worker).decode("utf-8")),
            namespace="/administration",
        )

    socketio.emit(
        "total_files",
        redis.get("total_files").decode("utf-8"),
        namespace="/administration",
    )
    socketio.emit(
        "total_files_processed",
        redis.get("total_files_processed").decode("utf-8"),
        namespace="/administration",
    )


@socketio.on("trash_file", namespace="/administration")
def trash_file(data):
    try:
        file_id = data.get("fileId")
        folder_id = data.get("folderId")
        with InterProcessLock(f"{current_app.root_path}/whoosh.lock"):
            Whoosh().delete_document(file_id)
        file = FICHIER.query.get(file_id)
        db.session.delete(file)
        os.remove(
            os.path.join(
                current_app.root_path,
                "storage",
                folder_id,
                f"{file_id}.{file.extension_Fichier}",
            )
        )
        db.session.commit()
        socketio.emit("file_deleted", data, namespace="/administration")
    except Exception as e:
        socketio.emit(
            "file_deletion_failed",
            {**data, "error": str(e)},
            namespace="/administration",
        )


@socketio.on("search_files", namespace="/administration")
def search_files(data):
    search_query = data.get("query")
    with InterProcessLock(f"{current_app.root_path}/whoosh.lock"):
        search_results = Whoosh().search(search_query, path=f'{data.get("folderId")}')
    socketio.emit("search_results", search_results, namespace="/administration")


@socketio.on("update_user_role", namespace="/administration")
def update_user_role(data):
    user_id = data.get("userId")
    role_id = data.get("roleId")
    user = UTILISATEUR.query.get(user_id)
    if user.id_Role == 1 and role_id != 1:
        data["roleId"] = 1
        socketio.emit(
            "user_role_not_updated",
            {**data, "error": "Le rôle de l'administrateur ne peut pas être modifié."},
            namespace="/administration",
        )
        return
    user.id_Role = role_id
    db.session.commit()
    socketio.emit(
        "user_role_updated",
        {**data, "message": "Le rôle de l'utilisateur a été modifié avec succès."},
        namespace="/administration",
    )


@socketio.on("update_user_status", namespace="/administration")
def update_user_status(data):
    user_id = data.get("userId")
    user = UTILISATEUR.query.get(user_id)
    if user.id_Role == 1:
        socketio.emit(
            "user_status_not_updated",
            {
                **data,
                "error": "Le statut de l'administrateur ne peut pas être modifié.",
            },
            namespace="/administration",
        )
        return
    user.est_Actif_Utilisateur = not user.est_Actif_Utilisateur
    db.session.commit()
    socketio.emit(
        "user_status_updated",
        {**data, "message": "Le statut de l'utilisateur a été modifié avec succès."},
        namespace="/administration",
    )


@socketio.on("delete_user", namespace="/administration")
def delete_user(data):
    user_id = data.get("userId")
    user = UTILISATEUR.query.get(user_id)
    if user.id_Role == 1:
        socketio.emit(
            "user_not_deleted",
            {**data, "error": "L'administrateur ne peut pas être supprimé."},
            namespace="/administration",
        )
        return
    db.session.delete(user)
    db.session.commit()
    socketio.emit(
        "user_deleted",
        {**data, "message": "L'utilisateur a été supprimé avec succès."},
        namespace="/administration",
    )

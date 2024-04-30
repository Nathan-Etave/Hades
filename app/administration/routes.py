import os
import json
from base64 import b64decode
from app import redis, socketio
from app.administration import bp
from app.tasks import process_file
from unidecode import unidecode
from flask import render_template, request, current_app, Response, jsonify
from flask_login import current_user
from werkzeug.utils import secure_filename
from flask_login import login_required
from app.decorators import admin_required
from app.extensions import db
from app.models.dossier import DOSSIER
from app.models.sous_dossier import SOUS_DOSSIER
from app.models.fichier import FICHIER
from app.models.utilisateur import UTILISATEUR
from app.models.a_acces import A_ACCES
from app.models.role import ROLE
from app.models.lien import LIEN
from app.utils import Whoosh, check_notitications
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
    all_links = LIEN.query.all()
    all_links = sorted(all_links, key=lambda x: x.nom_Lien.lower())
    return render_template(
        "administration/index.html",
        folders=all_root_folders,
        users=all_users,
        roles=all_roles,
        links=all_links,
        is_admin=True,
        is_authenticated=True,
        has_notifications=check_notitications(),
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
    existing_file = FICHIER.query.filter_by(nom_Fichier=filename).first()
    force = json_data.get("force")
    if existing_file is not None:
        if force:
            delete_file(str(existing_file.id_Fichier))
        else:
            return jsonify({'filename': filename,
                            'existingFolder': existing_file.DOSSIER_.nom_Dossier,
                            'attemptedFolder': DOSSIER.query.get(folder_id).nom_Dossier,
                            'existingFileAuthorFirstName': existing_file.AUTEUR.prenom_Utilisateur,
                            'existingFileAuthorLastName': existing_file.AUTEUR.nom_Utilisateur,
                            'existingFileDate': existing_file.date_Fichier.strftime('%d/%m/%Y à %H:%M')}), 409
    user_tags = unidecode(' '.join(json_data.get("tags").replace(' ', ';').split(';'))).lower()
    storage_directory = os.path.join(current_app.root_path, "storage")
    if not os.path.exists(f"{storage_directory}/{folder_id}"):
        os.makedirs(f"{storage_directory}/{folder_id}")
    file = FICHIER(
        id_Dossier=folder_id,
        nom_Fichier=filename,
        extension_Fichier=filename.split(".")[-1],
        id_Utilisateur=current_user.id_Utilisateur,
    )
    db.session.add(file)
    db.session.commit()
    file_path = os.path.join(
        storage_directory, folder_id, f"{file.id_Fichier}.{file.extension_Fichier}"
    )
    with open(file_path, "wb") as new_file:
        new_file.write(b64decode(file_data.split(",")[1]))
    process_file.apply_async(args=[file_path, filename, folder_id, str(file.id_Fichier), user_tags])
    redis.incr("total_files")
    redis.rpush(
        "file_queue", json.dumps({"file_id": file.id_Fichier, "filename": filename})
    )
    file_dict = file.to_dict()
    file_dict.update({"old_file_id": existing_file.id_Fichier if existing_file is not None else None})
    file_dict.update({"old_folder_id": existing_file.id_Dossier if existing_file is not None else None})
    return jsonify(file_dict), 200


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

@socketio.on('create_folder', namespace='/administration')
def create_folder(data):
    folder_name = data.get('folderName')
    parent_folder_id = data.get('parentFolderId')
    folder_roles = data.get('folderRoles')
    folder_color = data.get('folderColor')
    folder_priority = data.get('folderPriority')
    folders_to_update = DOSSIER.query.filter(DOSSIER.priorite_Dossier >= folder_priority).filter(DOSSIER.id_Dossier != 9).all()
    for folder_to_update in folders_to_update:
        folder_to_update.priorite_Dossier += 1
    folder = DOSSIER(nom_Dossier=folder_name, priorite_Dossier=folder_priority, couleur_Dossier=folder_color)
    db.session.add(folder)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folder_not_created', {'error': str(e)}, namespace='/administration')
        return
    try:
        db.session.execute(A_ACCES.insert().values(id_Role=1, id_Dossier=folder.id_Dossier))
        for role in folder_roles:
            db.session.execute(A_ACCES.insert().values(id_Role=role, id_Dossier=folder.id_Dossier))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.delete(folder)
        db.session.commit()
        socketio.emit('folder_not_created', {'error': str(e)}, namespace='/administration')
        return
    try:
        if parent_folder_id != 0:
            db.session.execute(SOUS_DOSSIER.insert().values(id_Dossier_Parent=parent_folder_id, id_Dossier_Enfant=folder.id_Dossier))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.execute(A_ACCES.delete().where(A_ACCES.c.id_Role == 1).where(A_ACCES.c.id_Dossier == folder.id_Dossier))
        for role in folder_roles:
            db.session.execute(A_ACCES.delete().where(A_ACCES.c.id_Role == role).where(A_ACCES.c.id_Dossier == folder.id_Dossier))
        db.session.delete(folder)
        db.session.commit()
        socketio.emit('folder_not_created', {'error': str(e)}, namespace='/administration')
        return
    socketio.emit('folder_created', {'folderId': folder.id_Dossier, 'folderName': folder_name, 'folderColor': folder.couleur_Dossier, 'parentFolderId': parent_folder_id}, namespace='/administration')

@socketio.on('modify_folder', namespace='/administration')
def modify_folder(data):
    folder_id = data.get('folderId')
    folder_name = data.get('folderName')
    parent_folder_id = data.get('parentFolderId')
    folder_roles = data.get('folderRoles')
    folder_priority = data.get('folderPriority')
    folder_color = data.get('folderColor')
    folder = DOSSIER.query.get(folder_id)
    folder.nom_Dossier = folder_name
    folder.couleur_Dossier = folder_color
    if folder.priorite_Dossier != int(folder_priority):
        if int(folder_priority) > folder.priorite_Dossier:
            folders_to_update = DOSSIER.query.filter(DOSSIER.priorite_Dossier > folder.priorite_Dossier).filter(DOSSIER.priorite_Dossier <= int(folder_priority)).filter(DOSSIER.id_Dossier != 9).all()
            for folder_to_update in folders_to_update:
                folder_to_update.priorite_Dossier -= 1
        else:
            folders_to_update = DOSSIER.query.filter(DOSSIER.priorite_Dossier >= int(folder_priority)).filter(DOSSIER.priorite_Dossier < folder.priorite_Dossier).filter(DOSSIER.id_Dossier != 9).all()
            for folder_to_update in folders_to_update:
                folder_to_update.priorite_Dossier += 1
        folder.priorite_Dossier = folder_priority
    try:
        if parent_folder_id == folder_id:
            socketio.emit('folder_not_modified', {'error': 'Un classeur ne peut pas être son propre parent.'}, namespace='/administration')
            return
        if parent_folder_id != 0:
            db.session.execute(SOUS_DOSSIER.delete().where(SOUS_DOSSIER.c.id_Dossier_Enfant == folder_id))
            db.session.execute(SOUS_DOSSIER.insert().values(id_Dossier_Parent=parent_folder_id, id_Dossier_Enfant=folder_id))
            db.session.commit()
        else:
            db.session.execute(SOUS_DOSSIER.delete().where(SOUS_DOSSIER.c.id_Dossier_Enfant == folder_id))
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folder_not_modified', {'error': str(e)}, namespace='/administration')
        return
    try:
        db.session.execute(A_ACCES.delete().where(A_ACCES.c.id_Dossier == folder_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folder_not_modified', {'error': str(e)}, namespace='/administration')
        return
    try:
        db.session.execute(A_ACCES.insert().values(id_Role=1, id_Dossier=folder_id))
        for role in folder_roles:
            db.session.execute(A_ACCES.insert().values(id_Role=role, id_Dossier=folder_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folder_not_modified', {'error': str(e)}, namespace='/administration')
        return
    db.session.commit()
    socketio.emit('folder_modified', {'folderId': folder_id, 'folderName': folder_name, 'folderColor': folder_color}, namespace='/administration')

@socketio.on('delete_folder', namespace='/administration')
def delete_folder(data):
    folder = DOSSIER.query.get(data.get('folderId'))
    if folder.id_Dossier == 9:
        socketio.emit('folder_not_deleted', {'error': 'Le classeur d\'archive ne peut pas être supprimé.'}, namespace='/administration')
        return
    if len(folder.DOSSIER_) > 0:
        socketio.emit('folder_not_deleted', {'error': 'Le classeur contient des sous-classeurs.'}, namespace='/administration')
        return
    if len(folder.FICHIER) > 0:
        socketio.emit('folder_not_deleted', {'error': 'Le classeur contient des fichiers.'}, namespace='/administration')
        return
    try:
        db.session.execute(SOUS_DOSSIER.delete().where(SOUS_DOSSIER.c.id_Dossier_Enfant == folder.id_Dossier))
        db.session.execute(SOUS_DOSSIER.delete().where(SOUS_DOSSIER.c.id_Dossier_Parent == folder.id_Dossier))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folder_not_deleted', {'error': str(e)}, namespace='/administration')
        return
    try:
        db.session.execute(A_ACCES.delete().where(A_ACCES.c.id_Dossier == folder.id_Dossier))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folder_not_deleted', {'error': str(e)}, namespace='/administration')
        return
    deleted_priority = folder.priorite_Dossier
    db.session.delete(folder)
    db.session.commit()
    folders_to_update = DOSSIER.query.filter(DOSSIER.priorite_Dossier > deleted_priority).filter(DOSSIER.id_Dossier != 9).all()
    for folder_to_update in folders_to_update:
        folder_to_update.priorite_Dossier -= 1
    db.session.commit()
    socketio.emit('folder_deleted', {'folderId': folder.id_Dossier}, namespace='/administration')


@socketio.on('archive_folders', namespace='/administration')
def archive_folders(data):
    folder_ids = data.get('folderIds')
    try:
        for folder_id in folder_ids:
            database_folder = DOSSIER.query.get(folder_id)
            if folder_id == '9':
                pass
            elif database_folder.DOSSIER != [] and database_folder.DOSSIER[0].id_Dossier == 0:
                pass
            elif database_folder.DOSSIER != [] and str(database_folder.DOSSIER[0].id_Dossier) in folder_ids:
                pass
            else:
                if database_folder.DOSSIER != []:
                    db.session.execute(SOUS_DOSSIER.delete().where(SOUS_DOSSIER.c.id_Dossier_Enfant == folder_id))
                db.session.execute(SOUS_DOSSIER.insert().values(id_Dossier_Parent=9, id_Dossier_Enfant=folder_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('folders_not_archived', {'error': str(e)}, namespace='/administration')
        return
    socketio.emit('folders_archived', {'folderIds': folder_ids}, namespace='/administration')

@socketio.on('delete_files', namespace='/administration')
def delete_files(data):
    file_ids = data.get('fileIds')
    try:
        for file_id in file_ids:
            with InterProcessLock(f"{current_app.root_path}/whoosh.lock"):
                Whoosh().delete_document(file_id)
            database_file = FICHIER.query.get(file_id)
            db.session.delete(database_file)
            os.remove(
                os.path.join(
                    current_app.root_path,
                    "storage",
                    str(database_file.id_Dossier),
                    f"{file_id}.{database_file.extension_Fichier}",
                )
            )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('files_not_deleted', {'error': str(e)}, namespace='/administration')
        return
    socketio.emit('files_deleted', {'fileIds': file_ids}, namespace='/administration')

def delete_file(file_id):
    with InterProcessLock(f"{current_app.root_path}/whoosh.lock"):
        Whoosh().delete_document(file_id)
    database_file = FICHIER.query.get(file_id)
    db.session.delete(database_file)
    os.remove(
        os.path.join(
            current_app.root_path,
            "storage",
            str(database_file.id_Dossier),
            f"{file_id}.{database_file.extension_Fichier}",
        )
    )
    db.session.commit()

@socketio.on('delete_link', namespace='/administration')
def delete_link(data):
    try:
        link = LIEN.query.get(data.get('linkId'))
        db.session.delete(link)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        socketio.emit('link_not_deleted', {'error': str(e)}, namespace='/administration')
        return
    socketio.emit('link_deleted', {'linkId': data.get('linkId')}, namespace='/administration')

@socketio.on('create_link', namespace='/administration')
def create_link(data):
    link_name = data.get('linkName')
    link_url = data.get('linkUrl')
    link_description = data.get('linkDescription')
    try:
        link = LIEN(nom_Lien=link_name, lien_Lien=link_url, description_Lien=link_description, id_Utilisateur=current_user.id_Utilisateur)
        db.session.add(link)
        db.session.commit()
        link_date = link.date_Lien.strftime('%d/%m/%Y à %H:%M')
    except Exception as e:
        db.session.rollback()
        socketio.emit('link_not_created', {'error': str(e)}, namespace='/administration')
        return
    socketio.emit('link_created', {'linkId': link.id_Lien, 'linkName': link_name, 'linkUrl': link_url, 'linkDescription': link_description, 'linkDate': link_date, 'linkAuthor': f'{current_user.prenom_Utilisateur} {current_user.nom_Utilisateur}'}, namespace='/administration')
import time
import os
from app.file_handler import bp
from flask import send_from_directory, abort, current_app, request, send_file
from app.models.fichier import FICHIER
from flask_login import current_user, login_required
from app import socketio
from app.extensions import db
from app.models.favoris import FAVORIS
from app.utils import FileDownloader
from app.decorators import admin_required
from threading import Timer

@bp.route('/classeur/<int:folder_id>/fichier/<int:file_id>', methods=['GET'])
@login_required
def file(folder_id, file_id):
    file = FICHIER.query.get(file_id)
    as_attachment = request.args.get('as_attachment', default=False, type=bool)
    if file is None:
        return abort(404)
    if file.DOSSIER_.id_Dossier != folder_id:
        return abort(404)
    if not any(current_user.id_Role == role.id_Role for role in file.DOSSIER_.ROLE):
        return abort(403)
    return send_from_directory(f'{current_app.root_path}/storage/{folder_id}', f'{file.id_Fichier}.{file.extension_Fichier}', as_attachment=as_attachment, download_name=file.nom_Fichier)


@socketio.on('get_files_details', namespace='/file_handler')
def get_files_details(data):
    files_id = data['files']
    favoris = db.session.query(FAVORIS.c.id_Fichier).filter(FAVORIS.c.id_Utilisateur == current_user.id_Utilisateur).all()
    favoris_ids = [favori.id_Fichier for favori in favoris]
    files = []
    for file_id in files_id:
        file = db.session.query(FICHIER).filter(FICHIER.id_Fichier == file_id).first()
        dict_file = file.to_dict()
        dict_file['id_Dossier'] = file.DOSSIER_.id_Dossier
        dict_file['is_favorite'] = file.id_Fichier in favoris_ids
        files.append(dict_file)
    socketio.emit('files_details', files, namespace='/file_handler')


@bp.route('/download/archive', methods=['POST'])
@login_required
@admin_required
def download_archive():
    zip_path = FileDownloader().create_zip(request.json['fileIds'])
    delete_file_after_delay(43200, zip_path)
    return send_file(zip_path, 'archive.zip', as_attachment=True)

def delete_file_after_delay(delay, path):
    def delete_file():
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    Timer(delay, delete_file).start()
from app.file_handler import bp
from flask import send_from_directory, abort, current_app, request
from app.models.fichier import FICHIER
from flask_login import current_user
from app import socketio
from app.extensions import db

@bp.route('/dossier/<int:folder_id>/fichier/<int:file_id>', methods=['GET'])
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
    files = []
    for file_id in files_id:
        file = db.session.query(FICHIER).filter(FICHIER.id_Fichier == file_id).first()
        dict_file = file.to_dict()
        dict_file['id_Dossier'] = file.DOSSIER_.id_Dossier
        files.append(dict_file)
    socketio.emit('files_details', files, namespace='/file_handler')
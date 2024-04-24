from app.file_handler import bp
from flask import send_from_directory, abort, current_app, request
from app.models.fichier import FICHIER
from flask_login import current_user, login_required

@bp.route('/dossier/<int:folder_id>/fichier/<int:file_id>', methods=['GET'])
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

@bp.route('/model/<path:filename>', methods=['GET'])
@login_required
def get_model(filename):
    return send_from_directory(f'{current_app.root_path}/static/models', filename, as_attachment=False)

@bp.route('/skybox/<path:filename>', methods=['GET'])
@login_required
def get_skybox(filename):
    return send_from_directory(f'{current_app.root_path}/static/skybox', filename, as_attachment=False)

@bp.route('/texture/<path:filename>', methods=['GET'])
@login_required
def get_texture(filename):
    return send_from_directory(f'{current_app.root_path}/static/textures', filename, as_attachment=False)
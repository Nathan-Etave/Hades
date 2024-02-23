import base64
import os
from app import app, nlp, job_statuses
from flask import render_template, request, redirect, url_for, make_response, send_file, jsonify, Response, current_app
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
from app.requests import *
from app.forms import *
from app import login_manager
from threading import Thread
import uuid
from unidecode import unidecode

process_functions = {
    'pdf': nlp.process_pdf,
    'docx': nlp.process_docx,
    'xlsx': nlp.process_sheet,
    'pptx': nlp.process_presentation,
    'txt': nlp.process_txt,
}

@app.after_request
def add_cookie(response):
    if not request.cookies.get('multiview_list'):
        response.set_cookie('multiview_list', ';')
    return response

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id_Role == 1:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return decorated_function

def background_recherche(job_id, application, recherche):
    with application.app_context():
        dossiers = get_root_dossiers_by_role(current_user.id_Role)
        dossiers.sort(key=lambda x: x.priorite_Dossier)
        for dossier in dossiers:
            if job_id not in job_statuses:
                job_statuses[job_id] = {}
            job_statuses[job_id][dossier.id_Dossier] = {
                'id': dossier.id_Dossier,
                'nom': dossier.nom_Dossier,
                'priorite': dossier.priorite_Dossier,
                'couleur': dossier.couleur_Dossier,
                'fichiers': [],
                'status': False
            }
        for dossier in dossiers:
            for fichier in dossier.FICHIER:
                if file_meets_conditions(fichier, process_recherche(recherche)):
                    job_statuses[job_id][dossier.id_Dossier]['fichiers'].append({
                        'id': fichier.id_Fichier,
                        'nom': fichier.nom_Fichier,
                        'extension': fichier.extension_Fichier,
                        'favori': current_user.get_id() in [user.id_Utilisateur for user in fichier.UTILISATEUR_]
                    })
            job_statuses[job_id][dossier.id_Dossier]['status'] = True

def process_recherche(recherche):
    or_conditions = recherche.split('|')
    conditions = [condition.split('&') for condition in or_conditions]
    conditions = [sublist for sublist in [[condition.strip() for condition in sublist if condition.strip()] for sublist in conditions] if sublist]
    return conditions

def file_meets_conditions(fichier, conditions):
    if len(conditions) == 0:
        return True
    elif len(conditions) == 1:
        bools = [is_any_tag(fichier, tag) for tag in conditions[0]]
        return all(bools)
    else:
        bools = [file_meets_conditions(fichier, [condition]) for condition in conditions]
        return any(bools)

def is_any_tag(fichier, nom_tag):
    return nom_tag in unidecode(fichier.nom_Fichier.lower()) or any(tag.nom_Tag == nom_tag for tag in fichier.A_TAG)

@app.route('/recherche', methods=['GET', 'POST'])
def recherche():
    if request.method == 'POST':
        recherche = request.form['search']
        job_id = str(uuid.uuid4())
        application = current_app._get_current_object()
        thread = Thread(target=background_recherche, args=(job_id, application, unidecode(recherche.lower())))
        thread.start()
        return render_template('recherche.html', job_id=job_id)
    else:
        return render_template('recherche.html')

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    if job_id in job_statuses:
        return jsonify({'job': job_statuses[job_id]})
    else:
        return jsonify({'job': 'inconnu'}), 404
    
@app.route('/administration', methods=['GET'])
def administration():
    return render_template('administration.html', dossiers=get_root_dossiers())

@app.route('/administration/dossier/<id_dossier>', methods=['PUT'])
def update_dossier_api(id_dossier):
    nom = request.json.get('nom', None)
    priorite = request.json.get('priorite', None)
    couleur = request.json.get('couleur', None)
    update_dossier(id_dossier, nom, couleur, priorite)
    return Response(status=204)

@app.route('/administration/dossier/<id_dossier>/fichier', methods=['POST'])
def add_file_api(id_dossier):
    if not os.path.exists(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        os.makedirs(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}')
    filename = secure_filename(request.get_json()['nom'])
    extension = filename.split('.')[-1]
    data_file = request.get_json()['data']
    file_path = f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}'
    base64_data = data_file.split(',')[1]
    decoded_data = base64.b64decode(base64_data)
    with open(file_path, 'wb') as file:
        file.write(decoded_data)
    if extension in process_functions:
        tags = process_functions[extension](file_path)
    else:
        tags = []
    add_file(base64.b64encode(open(file_path, 'rb').read()), filename, extension, tags, id_dossier)
    os.remove(file_path)
    return Response(status=200)

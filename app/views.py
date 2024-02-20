import os
from app import app, nlp, job_statuses
from flask import render_template, request, redirect, url_for, make_response, send_file, jsonify, Response
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
from app.requests import *
from app.forms import *
from app import login_manager
from threading import Thread
import uuid

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
        if get_user_by_id(current_user.get_id()).idRole == 1:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return decorated_function

def background_recherche(job_id, application):
    with application.app_context():
        dossiers = get_root_dossiers()
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
        # tri des dossiers selon la recherche
        for dossier in dossiers:
            for fichier in dossier.FICHIER:
                job_statuses[job_id][dossier.id_Dossier]['fichiers'].append({
                    'id': fichier.id_Fichier,
                    'nom': fichier.nom_Fichier,
                    'extension': fichier.extension_Fichier,
                    'data': fichier.DATA_.data
                })
            job_statuses[job_id][dossier.id_Dossier]['status'] = True
        
@app.route('/recherche', methods=['GET', 'POST'])
def recherche():
    if request.method == 'POST':
            job_id = str(uuid.uuid4())
            application = current_app._get_current_object()
            thread = Thread(target=background_recherche, args=(job_id,application))
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
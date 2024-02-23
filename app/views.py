import base64
import os
import uuid
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
from app.mail import mailInscription, mailOublie
from datetime import datetime
from io import BytesIO

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

@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    form_mdp = MdpOublieForm()
    form_login = LoginForm()
    user = get_user_by_email(form_login.mail.data)
    form_inscription = InscriptionForm()
    if form_inscription.validate_on_submit():
        passe= generate_password()
        password = generate_password_hash(passe).decode('utf-8')
        role = None
        est_Actif_Utilisateur=0
        if not already_exist_mail(form_inscription.mail.data):
            add_user(form_inscription.prenom.data, form_inscription.nom.data, form_inscription.mail.data,form_inscription.telephone.data,role, password,est_Actif_Utilisateur)
            create_notification(get_user_by_email(form_inscription.mail.data).id_Utilisateur, None, datetime.now(), "Inscription")
            # mailInscription(form_inscription.mail.data, passe)
    if form_login.validate_on_submit():
        if user:
            if check_password_hash(user.mdp_Utilisateur, form_login.mdp.data) and user.est_Actif_Utilisateur == 1:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                login_user(user, remember=True)
                return redirect(url_for('home'))
    return render_template('connexion.html', form_login=form_login, form_inscription=form_inscription, form_mdp=form_mdp)

@app.route('/deconnexion')
@login_required
def deconnexion():
    logout_user()
    return redirect(url_for('connexion'))

def background_recherche(job_id, application, recherche, id_role, id_user):
    with application.app_context():
        dossiers = get_root_dossiers_by_role(id_role)
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
                        'favori': id_user in [user.id_Utilisateur for user in fichier.UTILISATEUR_]
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

@app.route('/administration/dossiers', methods=['PUT'])
@login_required
@admin_required
def update_dossiers_api():
    ordre_dossiers = request.get_json()['dossiers']
    for priorite, id_dossier in enumerate(ordre_dossiers):
        update_dossier_priorite(id_dossier, priorite + 1)
    return Response(status=204)

@app.route('/recherche', methods=['GET', 'POST'])
@login_required
def recherche():
    if request.method == 'POST':
        recherche = request.form['search']
        create_recherche(recherche, current_user.get_id())
        job_id = str(uuid.uuid4())
        application = current_app._get_current_object()
        thread = Thread(target=background_recherche, args=(job_id, application, unidecode(recherche.lower()), current_user.id_Role, current_user.get_id()))
        thread.start()
        return render_template('recherche.html', job_id=job_id, is_admin=current_user.id_Role == 1)
    else:
        return render_template('recherche.html', is_admin=current_user.id_Role == 1)

@app.route('/status/<job_id>', methods=['GET'])
@login_required
def status(job_id):
    if job_id in job_statuses:
        return jsonify({'job': job_statuses[job_id]})
    else:
        return jsonify({'job': 'inconnu'}), 404

@app.route('/administration', methods=['GET', 'DELETE', 'PUT'])
@login_required
@admin_required
def administration():
    if request.method == 'GET':
        dossiers = get_root_dossiers()
        dossiers.sort(key=lambda x: x.priorite_Dossier)
        return render_template('administration.html', dossiers=dossiers, utilisateurs=get_all_users(), is_admin=current_user.id_Role == 1)
    elif request.method == 'DELETE':
        json = request.get_json()
        id_dossier = json['id']
        delete_utilisateur(id_dossier)
        return jsonify({'status': 'ok'})
    elif request.method == 'PUT':
        json = request.get_json()
        id_utilisateur = json['id']
        update_role(id_utilisateur)
        return jsonify({'status': 'ok'})

@app.route('/administration/dossier/<id_dossier>', methods=['PUT'])
@login_required
@admin_required
def update_dossier_api(id_dossier):
    nom = request.json.get('nom', None)
    priorite = request.json.get('priorite', None)
    couleur = request.json.get('couleur', None)
    update_dossier(id_dossier, nom, couleur, priorite)
    return Response(status=204)

@app.route('/administration/dossier/<id_dossier>/fichier', methods=['POST'])
@login_required
@admin_required
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

@app.route('/')
@login_required
def home():
    liste_fav = current_user.FICHIER_
    liste_recherche = current_user.A_RECHERCHE
    return render_template('index.html', liste_fav=liste_fav, liste_recherche=liste_recherche, is_admin=current_user.id_Role == 1)

@app.route('/previsualisation/<id_fichier>' , methods=['GET'])
@login_required
def previsualisation(id_fichier):
    data = get_data_by_file_id(id_fichier)
    return data.data

@app.route('/unfavorize', methods=['POST'])
@login_required
def unfavorize():
    json = request.get_json()
    id_file = json['id']
    unfavorite_file(id_file, current_user.get_id())
    return jsonify({'status': 'ok'})

@app.route('/favorize', methods=['POST'])
@login_required
def favorize():
    json = request.get_json()
    id_file = json['id']
    favorite_file(id_file, current_user.get_id())
    return jsonify({'status': 'ok'})

@app.route('/download', methods=['POST'])
@login_required
def download():
    json = request.get_json()
    id_file = json['id']
    print(id_file)
    data = get_data_from_file_id(id_file)
    return make_response(send_file(BytesIO(data.data), mimetype='application/octet-stream'))

@app.route('/add_multiview', methods=['POST'])
@login_required
def add_multiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['id']
    if f';{file_id};' not in multiview_list:
        multiview_list += f'{file_id};'
    response = app.make_response(redirect(url_for('home')))
    response.set_cookie('multiview_list', multiview_list)
    return response

@app.route('/unmultiview', methods=['POST'])
@login_required
def unmultiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['id']
    multiview_list = multiview_list.replace(f';{file_id};', ';')
    response = app.make_response(redirect(url_for('home')))
    response.set_cookie('multiview_list', multiview_list)
    return response

@app.route('/multivue')
@login_required
def multivue():
    return

@app.route('/user')
@login_required
def user():
    return

@app.route('/notifications')
@login_required
def notifications():
    return
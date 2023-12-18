import os
from app import app, nlp
from flask import render_template, request, redirect, url_for, make_response, send_file, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from io import BytesIO
from functools import wraps
from werkzeug.utils import secure_filename
from app.requests import (get_root_categories, get_user_by_id, get_user_by_email,get_user_favourites_file,
                          get_file_by_id, user_has_notifications, add_to_user_favourites, remove_from_user_favourites,
                          add_administrator_signalement, get_user_notifications, update_user, get_file_order_by_date,
                          update_user_photo, remove_from_user_notification, get_file_by_tag, get_all_files, get_file_history,
                          get_file_by_categorie, get_file_tags, get_category_tree, add_file_to_database)

from app.forms import LoginForm, EditUserForm
from app import login_manager
import base64
import collections

@app.after_request
def add_cookie(response):
    if not request.cookies.get('multiview_list'):
        response.set_cookie('multiview_list', ';')
    if not request.cookies.get('favourites_list'):
        response.set_cookie('favourites_list', ';')
    else:
        favourites_list = get_user_favourites_file(current_user.get_id())
        favourites_list = ''.join([f';{f.idFichier}' for f in favourites_list]) + ';'
        response.set_cookie('favourites_list', favourites_list)
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user = get_user_by_email(form.mail.data)
    if form.validate_on_submit():
        if user:
            if check_password_hash(user.mdpPompier, form.mdp.data):
                login_user(user, remember=True)
                return redirect(url_for('home'))
    return render_template('connexion.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html', nom_page='Accueil', liste_categories=get_root_categories(), liste_fichiers=get_user_favourites_file(current_user.get_id()), notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        favourites_sort = request.form.get('favoris', False)
        recent_sort = request.form.get('recent', False)
        advanced_sort = request.form.get('advanced_search', False)
        categorie_id = request.form.get('categorie', '')
        return redirect(url_for('search', search=search_term, categorie=categorie_id,favoris=favourites_sort, recent=recent_sort, advanced_search=advanced_sort))
    else:
        search_term = request.args.get('search', type=str, default='')
        favourites_sort = request.args.get('favoris', type=bool, default='')
        recent_sort = request.args.get('recent', type=bool, default='')
        advanced_sort = request.args.get('advanced_search', type=bool, default='')
        categorie_id = request.args.get('categorie', type=int, default='')
        liste_fichiers_search_term = []
        liste_fichiers_recent_sort = []
        liste_fichiers_favourites_sort = []
        liste_fichiers_categorie_sort = []
        liste_fichiers_extension_sort = []
        liste_fichiers_advanced_sort = []
        if search_term :
            liste_fichiers_search_term = get_file_by_tag(search_term)
        if recent_sort :
            liste_fichiers_recent_sort = get_file_order_by_date(current_user.get_id())
        if favourites_sort :
            liste_fichiers_favourites_sort = get_user_favourites_file(current_user.get_id())
        if advanced_sort :
            liste_fichiers_advanced_sort = get_all_files()
        if categorie_id :
            liste_fichiers_categorie_sort = get_file_by_categorie(categorie_id)
        counter_list = [collections.Counter(liste_fichiers_recent_sort), collections.Counter(liste_fichiers_favourites_sort),
                        collections.Counter(liste_fichiers_search_term), collections.Counter(liste_fichiers_advanced_sort), collections.Counter(liste_fichiers_categorie_sort)]
        counter_list = [counter for counter in counter_list if counter]
        if len(counter_list) == 0:
            liste_fichiers = []
        else :
            while counter_list:
                result = counter_list.pop(0)
                for counter in counter_list:
                    result &= counter
                liste_fichiers = list(result.elements())
        return render_template('search.html', nom_page=search_term, categorie=get_root_categories()[0], liste_fichiers=liste_fichiers, notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/file')
@login_required
def file():
    return render_template('file.html' , nom_page='Consultation de fichier', fichier=get_file_by_id(request.args.get('id_fichier', type=int, default='')), liste_tags=get_file_tags(request.args.get('id_fichier', type=int, default='')), notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/add_to_multiview', methods=['POST'])
@login_required
def add_to_multiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['file_id']
    if f';{file_id};' not in multiview_list:
        multiview_list += f'{file_id};'
    response = app.make_response(redirect(url_for('login')))
    response.set_cookie('multiview_list', multiview_list)
    return response

@app.route('/remove_from_multiview', methods=['POST'])
@login_required
def remove_from_multiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['file_id']
    multiview_list = multiview_list.replace(f';{file_id};', ';')
    response = app.make_response(redirect(url_for('login')))
    response.set_cookie('multiview_list', multiview_list)
    return response

@app.route('/add_to_favourites', methods=['POST'])
@login_required
def add_to_favourites():
    file_id = request.get_json()['file_id']
    add_to_user_favourites(current_user.get_id(), file_id)
    return redirect(url_for('login'))

@app.route('/remove_from_favourites', methods=['POST'])
@login_required
def remove_from_favourites():
    file_id = request.get_json()['file_id']
    remove_from_user_favourites(current_user.get_id(), file_id)
    return redirect(url_for('login'))

@app.route('/remove_from_notifications', methods=['POST'])
@login_required
def remove_from_notifications():
    id_notification = request.get_json()['id_notification']
    id_file = request.get_json()['id_file']
    id_date = request.get_json()['id_date']
    remove_from_user_notification(id_notification, id_file, id_date, current_user.get_id())
    return redirect(url_for('login'))

@app.route('/report', methods=['POST'])
@login_required
def report():
    file_id = request.get_json()['file_id']
    description = request.get_json()['reason']
    add_administrator_signalement(file_id, current_user.get_id(), description)
    return redirect(url_for('login'))

@app.route('/download_file', methods=['POST'])
@login_required
def download_file():
    file_id = request.get_json()['file_id']
    file_object = get_file_by_id(file_id)
    return make_response(send_file(BytesIO(file_object.data), mimetype='application/octet-stream'))

@app.route('/multivue', methods=['GET', 'POST'])
@login_required
def multivue():
    liste_mv = request.cookies.get('multiview_list').split(';')
    liste_fich = []
    for id_fichier in liste_mv:
        if id_fichier != '':
            fichiers = get_file_by_id(int(id_fichier))
            if fichiers:
                liste_fich.append(fichiers)
    file_index = request.args.get('file_index', default=None, type=int)
    fichier_selected = None
    if file_index is None and liste_fich:
        fichier_selected = liste_fich[0]
        file_index = fichier_selected.idFichier
    else :
        fichier_selected = None
        for fichier in liste_fich:
            if fichier.idFichier == file_index:
                fichier_selected = fichier
    return render_template('multivue.html',
                        nom_page="MultiVue",
                        liste_fichiers=liste_fich,
                        index_selected=file_index,
                        liste_tags=get_file_tags(fichier_selected.idFichier if fichier_selected else None),
                        fichier_selected=fichier_selected, notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/user')
@login_required
def user():
    user = get_user_by_id(current_user.get_id())
    page_name = f'Profil : {user.nomPompier} {user.prenomPompier}'
    return render_template('user.html', user = user, nom_page=page_name, notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/editUser', methods=['GET', 'POST'])
@login_required
def editUser():
    user = get_user_by_id(current_user.get_id())
    form = EditUserForm(id=user.idPompier, nom=user.nomPompier, prenom=user.prenomPompier, mail=user.emailPompier, mdp=user.mdpPompier, photo=user.photoPompier,telephone=user.telephonePompier)
    page_name = f'Modifier le profil : {user.nomPompier} {user.prenomPompier}'
    if form.validate_on_submit():
        password = generate_password_hash(form.mdp.data).decode('utf-8')
        if form.photo.data:
            encoded_photo = base64.b64encode(form.photo.data.read())
            update_user_photo(user.idPompier, encoded_photo)
        update_user(user.idPompier, form.prenom.data, form.nom.data, form.mail.data, form.telephone.data, password)
        return redirect(url_for('user'))
    return render_template('editUser.html', nom_page=page_name, user=user, form=form, notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/notifications')
@login_required
def notifications():
    notif = get_user_notifications(current_user.get_id())
    return render_template('notifications.html', nom_page="Notification(s)", liste_notifications=notif, notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/history')
@login_required
def history():
    id_file = request.args.get('id_fichier', type=int, default='')
    history_list = get_file_history(id_file)
    return render_template('history.html', nom_page=f"Historique de {get_file_by_id(id_file).nomFichier}", liste_fichiers=history_list, notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload():
    if not os.path.exists(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        os.makedirs(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}')
    if request.method == 'POST':
        for key, uploaded_file in request.files.items():
            if key.startswith('file'):
                filename = secure_filename(uploaded_file.filename)
                uploaded_file.save(os.path.join(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}', filename))
    else:
        for stored_file in os.listdir(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
            os.remove(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{stored_file}')
    return render_template('upload.html', nom_page="Ajouter un/des fichier(s)", notification_enabled=user_has_notifications(current_user.get_id()))

@app.route('/manage_files')
@login_required
@admin_required
def manageFiles():
    stored_files = {}
    for stored_file in os.listdir(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        stored_files[stored_file] = base64.b64encode(open(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{stored_file}', 'rb').read())
    return render_template('manageFiles.html', nom_page="Gestion des fichiers ajoutés", stored_files=stored_files, notification_enabled=user_has_notifications(current_user.get_id()), category_tree=get_category_tree())

@app.route('/automatic_files_management')
@login_required
@admin_required
def automaticFilesManagement():
    return 'A implémenter'

@app.route('/generate_tags', methods=['POST'])
@login_required
@admin_required
def generateTags():
    filename = request.get_json()['filename']
    extension = filename.split('.')[-1]
    file_path = f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}'
    tags = []
    if extension == 'pdf':
        tags = nlp.process_pdf(file_path)
    elif extension == 'docx':
        tags = nlp.process_docx(file_path)
    elif extension == 'xlsx' or extension == 'xls':
        tags = nlp.process_sheet(file_path)
    elif extension == 'pptx':
        tags = nlp.process_presentation(file_path)
    return jsonify(tags)

@app.route('/upload_files_to_database', methods=['POST'])
@login_required
@admin_required
def uploadFilesToDatabase():
    for filename, file_properties in request.get_json().items():
        file_path = f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}'
        extension = filename.split('.')[-1]
        with open(file_path, 'rb') as file_data:
            add_file_to_database(base64.b64encode(file_data.read()), filename, extension, file_properties['tags'], file_properties['categories'], 2)
    return redirect(url_for('upload'))
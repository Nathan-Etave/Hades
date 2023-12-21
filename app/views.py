import os
from app import app, nlp
from flask import render_template, request, redirect, url_for, make_response, send_file, jsonify, Response
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from io import BytesIO
from functools import wraps
from unidecode import unidecode
from werkzeug.utils import secure_filename
from app.requests import (get_root_categories, get_user_by_id, get_user_by_email,get_user_favourites_file,
                          get_file_by_id, user_has_notifications, add_to_user_favourites, remove_from_user_favourites,
                          add_administrator_signalement, get_user_notifications, update_user, get_file_order_by_date,
                          update_user_photo, remove_from_user_notification, get_file_by_tag, get_all_files, get_file_history,
                          get_file_by_categorie, get_file_tags, get_category_tree, add_file_to_database, add_consulted_file,
                          add_category_to_database, update_category_from_database, remove_category_from_database,
                          get_file_category_leaves, update_old_file, remove_file, update_file_categories, update_file_tags,
                          get_file_by_extension, get_all_extension, remove_forbiden_file, desactivate_user, get_all_roles, add_user,
                          get_user_by_name)
from app.forms import LoginForm, EditUserForm, AddUserForm
from app import login_manager
import base64
import collections

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

def activated_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_user_by_id(current_user.get_id()).idRole != 2:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
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
@activated_required
@login_required
def home():
    return render_template('home.html', nom_page='Accueil', liste_categories=get_root_categories(), liste_fichiers=get_user_favourites_file(current_user.get_id()), notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

def intersect_files(file_lists):
    file_lists = [lst for lst in file_lists if "vide" not in lst]
    if not file_lists:
        return []
    intersection = file_lists[0]
    for file in intersection.copy():
        if not all(any(file.nomFichier == other_file.nomFichier for other_file in lst) for lst in file_lists[1:]):
            intersection.remove(file)
    return intersection

def unique_files(file_list):
    unique_list = []
    seen_files = []
    for file in file_list:
        if file.nomFichier not in seen_files:
            seen_files.append(file.nomFichier)
            unique_list.append(file)
    return unique_list

@app.route('/search', methods=['GET', 'POST'])
@activated_required
@login_required
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        favourites_sort = request.form.get('favoris', '')
        recent_sort = request.form.get('recent', '')
        categorie_id = request.form.get('categorie', '')
        extension = request.form.get('extension', '')
        return redirect(url_for('search', search=search_term, categorie=categorie_id,favoris=favourites_sort, recent=recent_sort, extension=extension))
    else:
        # Recupération des paramètres de recherche
        search_term = request.args.get('search', type=str, default='')
        favourites_sort = request.args.get('favoris', type=bool, default='')
        recent_sort = request.args.get('recent', type=bool, default='')
        categorie_id = request.args.get('categorie', type=int, default='')
        extension = request.args.get('extension', type=str, default='')
        
        liste_fichiers_favourites_sort = ["vide"]
        liste_fichiers_search_term = ["vide"]
        liste_fichiers_categories = ["vide"]
        liste_recent_sort = ["vide"]
        liste_extension_sort = ["vide"]
        
        #Remplissage des listes de fichiers
        if favourites_sort :
            liste_fichiers_favourites_sort = get_user_favourites_file(current_user.get_id())
        if search_term :
            liste_fichiers_search_term = get_file_by_tag(unidecode(search_term))
        if categorie_id :
            liste_fichiers_categories = get_file_by_categorie(categorie_id)
        if recent_sort :
            liste_recent_sort = get_file_order_by_date(current_user.get_id())
        if extension :
            liste_extension_sort = get_file_by_extension(extension)
        
        #Intersection des listes de fichiers et tri
        counter_list = [liste_recent_sort, liste_fichiers_favourites_sort, liste_fichiers_search_term, liste_fichiers_categories, liste_extension_sort]
        liste_fichiers = intersect_files(counter_list)
        liste_fichiers.reverse()
        liste_fichiers = unique_files(liste_fichiers)

        #Si aucune recherche n'est faite, on affiche tous les fichiers
        if not favourites_sort and not recent_sort and not categorie_id and not search_term and not extension:
            liste_fichiers = get_all_files()
            
        #on retire les fichiers que l'on ne doit pas voir
        liste_fichiers = remove_forbiden_file(liste_fichiers,current_user.get_id())

        return render_template('search.html', nom_page=search_term, categorie=get_root_categories()[0], liste_fichiers=liste_fichiers, notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1,liste_extensions=get_all_extension(), category_tree=get_category_tree())

@app.route('/file')
@activated_required
@login_required
def file():
    add_consulted_file(current_user.get_id(), request.args.get('id_fichier', type=int, default=''))
    return render_template('file.html' , nom_page='Consultation de fichier', fichier=get_file_by_id(request.args.get('id_fichier', type=int, default='')),
                           liste_tags=get_file_tags(request.args.get('id_fichier', type=int, default='')),
                           notification_enabled=user_has_notifications(current_user.get_id()), is_admin=get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/add_to_multiview', methods=['POST'])
@activated_required
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
@activated_required
@login_required
def remove_from_multiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['file_id']
    multiview_list = multiview_list.replace(f';{file_id};', ';')
    response = app.make_response(redirect(url_for('login')))
    response.set_cookie('multiview_list', multiview_list)
    return response

@app.route('/add_to_favourites', methods=['POST'])
@activated_required
@login_required
def add_to_favourites():
    file_id = request.get_json()['file_id']
    add_to_user_favourites(current_user.get_id(), file_id)
    return redirect(url_for('login'))

@app.route('/remove_from_favourites', methods=['POST'])
@activated_required
@login_required
def remove_from_favourites():
    file_id = request.get_json()['file_id']
    remove_from_user_favourites(current_user.get_id(), file_id)
    return redirect(url_for('login'))

@app.route('/remove_from_notifications', methods=['POST'])
@activated_required
@login_required
def remove_from_notifications():
    id_notification = request.get_json()['id_notification']
    id_file = request.get_json()['id_file']
    id_date = request.get_json()['id_date']
    remove_from_user_notification(id_notification, id_file, id_date, current_user.get_id())
    return redirect(url_for('notifications'))

@app.route('/report', methods=['POST'])
@activated_required
@login_required
def report():
    file_id = request.get_json()['file_id']
    description = request.get_json()['reason']
    add_administrator_signalement(file_id, current_user.get_id(), description)
    return redirect(url_for('login'))

@app.route('/download_file', methods=['POST'])
@activated_required
@login_required
def download_file():
    file_id = request.get_json()['file_id']
    file_object = get_file_by_id(file_id)
    return make_response(send_file(BytesIO(file_object.data), mimetype='application/octet-stream'))

@app.route('/multivue', methods=['GET', 'POST'])
@activated_required
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
                        fichier_selected=fichier_selected, notification_enabled=user_has_notifications(current_user.get_id()),
                        is_admin=get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/user')
@activated_required
@login_required
def user():
    user = get_user_by_id(current_user.get_id())
    page_name = f'Profil : {user.nomPompier} {user.prenomPompier}'
    return render_template('user.html', user = user, nom_page=page_name, notification_enabled=user_has_notifications(current_user.get_id()), is_admin=get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/editUser', methods=['GET', 'POST'])
@activated_required
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
    return render_template('editUser.html', nom_page=page_name, user=user, form=form, notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/notifications')
@activated_required
@login_required
def notifications():
    notif = get_user_notifications(current_user.get_id())
    return render_template('notifications.html', nom_page="Notification(s)", liste_notifications=notif, notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/history')
@activated_required
@login_required
def history():
    id_file = request.args.get('id_fichier', type=int, default='')
    history_list = get_file_history(id_file)
    return render_template('history.html', nom_page=f"Historique de {get_file_by_id(id_file).nomFichier}", liste_fichiers=history_list, notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/upload', methods=['GET', 'POST'])
@activated_required
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
    return render_template('upload.html', nom_page="Ajouter un/des fichier(s)", notification_enabled=user_has_notifications(current_user.get_id()), is_admin=get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/manage_files')
@activated_required
@login_required
@admin_required
def manageFiles():
    stored_files = {}
    for stored_file in os.listdir(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        stored_files[stored_file] = base64.b64encode(open(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{stored_file}', 'rb').read())
    return render_template('manageFiles.html', nom_page="Gestion des fichiers ajoutés", stored_files=stored_files, notification_enabled=user_has_notifications(current_user.get_id()), category_tree=get_category_tree(), is_admin=get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/automatic_files_management', methods=['POST'])
@activated_required
@login_required
@admin_required
def automaticFilesManagement():
    custom_tags = request.get_json()['tags'].split(';')
    if custom_tags == ['']:
        custom_tags = []
    elif '' in custom_tags:
        custom_tags.remove('')
    custom_tags = list(dict.fromkeys(custom_tags))
    stored_files = {}
    for stored_file in os.listdir(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        stored_files[stored_file] = base64.b64encode(open(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{stored_file}', 'rb').read())
    for filename, file_data in stored_files.items():
        extension = filename.split('.')[-1]
        filename_tags = []
        tags = []
        filename_tags.append(filename.split('.')[0])
        filename_tags.append(filename)
        if extension in process_functions:
            tags = process_functions[extension](f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}')
            tags.extend(custom_tags)
            tags.extend(filename_tags)
        else:
            tags = custom_tags.copy()
            tags.extend(filename_tags)
        add_file_to_database(file_data, filename, extension, tags, [1], 2)
    return redirect(url_for('upload'))

@app.route('/generate_tags', methods=['POST'])
@activated_required
@login_required
@admin_required
def generateTags():
    filename = request.get_json()['filename']
    extension = filename.split('.')[-1].lower()
    file_path = f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}'
    tags = []
    if extension in process_functions:
        tags = process_functions[extension](file_path)
    return jsonify(tags)

@app.route('/upload_files_to_database', methods=['POST'])
@activated_required
@login_required
@admin_required
def uploadFilesToDatabase():
    for filename, file_properties in request.get_json().items():
        file_path = f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}'
        extension = filename.split('.')[-1]
        with open(file_path, 'rb') as file_data:
            add_file_to_database(base64.b64encode(file_data.read()), filename, extension, file_properties['tags'], file_properties['categories'], 2)
    return redirect(url_for('upload'))
  
@app.route('/edit_categories')
@activated_required
@login_required
@admin_required
def edit_categories():
    return render_template('editCategories.html', nom_page="Modifier les catégories", notification_enabled=user_has_notifications(current_user.get_id()), category_tree=get_category_tree(), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/add_category', methods=['POST'])
@activated_required
@login_required
@admin_required
def add_category():
    json = request.get_json()
    category_name = json['categoryName']
    parent_id = json['parentId']
    add_category_to_database(category_name, parent_id)
    return redirect(url_for('edit_categories'))

@app.route('/update_category', methods=['POST'])
@activated_required
@login_required
@admin_required
def update_category():
    json = request.get_json()
    category_id = json['categoryId']
    category_name = json['categoryName']
    update_category_from_database(category_id, category_name)
    return redirect(url_for('edit_categories'))

@app.route('/delete_category', methods=['POST'])
@activated_required
@login_required
@admin_required
def delete_category():
    json = request.get_json()
    category_id = json['categoryId']
    remove_category_from_database(category_id)
    return redirect(url_for('edit_categories'))

@app.route('/edit_file', methods=['POST', 'GET'])
@activated_required
@login_required
@admin_required
def edit_file():
    if not os.path.exists(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        os.makedirs(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}')
    file_id = request.args.get('id_fichier', type=int, default='')
    file_object = get_file_by_id(file_id)
    file_tags = get_file_tags(file_id)
    file_categories_leaves = get_file_category_leaves(file_id)
    temp_file_path = f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{file_object.nomFichier}'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(base64.b64decode(file_object.data))
    return render_template('editFile.html', nom_page=f"Modifier {file_object.nomFichier}", fichier=file_object, notification_enabled=user_has_notifications(current_user.get_id()),
                           category_tree=get_category_tree(), file_tags=file_tags, file_categories_leaves=file_categories_leaves, is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/add_file_to_temp', methods=['POST'])
@activated_required
@login_required
@admin_required
def add_file_to_temp():
    if not os.path.exists(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        os.makedirs(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}')
    json = request.get_json()
    uploaded_file = json['fileData']
    filename = secure_filename(json['filename'])
    with open(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{filename}', 'wb') as temp_file:
        temp_file.write(base64.b64decode(uploaded_file.split(',')[1]))
    return jsonify(filename)

@app.route('/update_file', methods=['POST'])
@activated_required
@login_required
@admin_required
def update_file():
    json = request.get_json()
    for filename, file_properties in json.items():
        extension = filename.split('.')[-1]
        tags = file_properties['tags']
        categories = file_properties['categories']
        will_be_updated = file_properties['willBeUpdated']
        will_be_deleted = file_properties['willBeDeleted']
        old_file_id = file_properties['oldFileId']
        file_data = file_properties['fileData']
        if will_be_updated:
            new_id = update_old_file(bytes(file_data.split(',')[1], 'utf-8'),
                                     filename, extension, tags, categories, 2, old_file_id)
            return redirect(url_for('file', id_fichier=new_id))
        elif will_be_deleted:
            remove_file(old_file_id)
        else:
            update_file_categories(old_file_id, categories)
            update_file_tags(old_file_id, tags)
            return redirect(url_for('file', id_fichier=old_file_id))
    return redirect(url_for('home'))

@app.route('/delete_all_temp_files', methods=['POST'])
@activated_required
@login_required
@admin_required
def delete_all_temp_files():
    for stored_file in os.listdir(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}'):
        os.remove(f'{app.config["UPLOADED_TEMP_DEST"]}/{current_user.get_id()}/{stored_file}')
    return Response(status=204)

@app.route('/search_user', methods=['GET', 'POST'])
@activated_required
@login_required
@admin_required
def search_user():
    if request.method == 'POST':
        try:
            id = request.form['searchId']
            return redirect(url_for('edit_profil_admin', user=id))
        except:
            try:
                email = unidecode(request.form['searchEmail'])
                return redirect(url_for('edit_profil_admin', user=get_user_by_email(email).idPompier))
            except:
                try:
                    nom,prenom = request.form['searchNom'],request.form['searchPrenom']
                    return redirect(url_for('edit_profil_admin', user=get_user_by_nom(nom,prenom).idPompier))
                except:
                    return redirect(url_for('search_user', error=True))
    else:
        user = get_user_by_id(current_user.get_id())
        error = request.args.get('error', type=bool, default=False)
        return render_template("searchUser.html",user = user,error = error,notification_enabled=user_has_notifications(current_user.get_id()),  is_admin =get_user_by_id(current_user.get_id()).idRole == 1)
    
@app.route('/edit_profil_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profil_admin():
    user = get_user_by_id(request.args.get('user', type=int, default=''))
    if user is None:
        user = get_user_by_email(request.args.get('user', type=str, default=''))
        if user is None:
            return redirect(url_for('search_user', error=True))
    form = EditUserForm(id=user.idPompier, nom=user.nomPompier, prenom=user.prenomPompier, mail=user.emailPompier, mdp=user.mdpPompier, photo=user.photoPompier,telephone=user.telephonePompier)
    page_name = f'Modifier le profil : {user.nomPompier} {user.prenomPompier}'
    if form.validate_on_submit():
        password = generate_password_hash(form.mdp.data).decode('utf-8')
        if form.photo.data:
            role = int(request.form.get('role',2)[0])
            encoded_photo = base64.b64encode(form.photo.data.read())
            update_user_photo(user.idPompier, encoded_photo)
        update_user(user.idPompier, form.prenom.data, form.nom.data, form.mail.data, form.telephone.data, password,role)
        return redirect(url_for('administration'))
    return render_template('editUser.html', nom_page=page_name, user=user,roles=get_all_roles(), form=form, notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/administration')
@activated_required
@login_required
@admin_required
def administration():
    return render_template('administration.html', nom_page="Administration", notification_enabled=user_has_notifications(current_user.get_id()), is_admin=get_user_by_id(current_user.get_id()).idRole == 1)

@app.route('/edit_role')
@activated_required
@login_required
@admin_required
def edit_role():
    return 'À implémenter'

@app.route('/del_user')
@activated_required
@login_required
@admin_required
def delUser():
    id = request.args.get('user', type=int, default='')
    desactivate_user(id)
    return redirect(url_for('administration'))

@app.route('/add_user', methods=['GET', 'POST'])
@activated_required
@login_required
@admin_required
def add_user_page():
    form = AddUserForm()
    if form.validate_on_submit():
        role = int(request.form.get('role', 2)[0])
        password = generate_password_hash(form.mdp.data).decode('utf-8')
        add_user(form.prenom.data, form.nom.data, form.mail.data,form.telephone.data,role, password)
        return redirect(url_for('administration'))
    return render_template('addUser.html', form=form,roles=get_all_roles(), notification_enabled=user_has_notifications(current_user.get_id()), is_admin =get_user_by_id(current_user.get_id()).idRole == 1)

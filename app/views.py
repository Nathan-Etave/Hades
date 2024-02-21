import os
from app import app, nlp
from flask import render_template, request, redirect, url_for, make_response, send_file, jsonify, Response
from flask_login import login_required, login_user, logout_user, current_user
from flask_bcrypt import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
from app.requests import *
from app.forms import *
from app import login_manager
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
        if get_user_by_id(current_user.get_id()).idRole == 1:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return decorated_function

@app.route('/')
def home():
    liste_fav = get_files_favoris(1)
    return render_template('index.html', liste_fav=liste_fav)

@app.route('/unfavorize', methods=['POST'])
def unfavorize():
    json = request.get_json()
    id_file = json['id']
    unfavorite_file(id_file, 1)
    return jsonify({'status': 'ok'})

@app.route('/favorize', methods=['POST'])
def favorize():
    json = request.get_json()
    id_file = json['id']
    favorite_file(id_file, 1)
    return jsonify({'status': 'ok'})

@app.route('/download', methods=['POST'])
def download():
    json = request.get_json()
    id_file = json['id']
    print(id_file)
    data = get_data_from_file_id(id_file)
    return make_response(send_file(BytesIO(data.data), mimetype='application/octet-stream'))

@app.route('/add_multiview', methods=['POST'])
def add_multiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['id']
    if f';{file_id};' not in multiview_list:
        multiview_list += f'{file_id};'
    response = app.make_response(redirect(url_for('home')))
    response.set_cookie('multiview_list', multiview_list)
    return response

@app.route('/unmultiview', methods=['POST'])
def unmultiview():
    multiview_list = request.cookies.get('multiview_list')
    file_id = request.get_json()['id']
    multiview_list = multiview_list.replace(f';{file_id};', ';')
    response = app.make_response(redirect(url_for('home')))
    response.set_cookie('multiview_list', multiview_list)
    return response
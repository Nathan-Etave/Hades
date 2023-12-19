import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_dropzone import Dropzone

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nathan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.normpath(os.path.join(os.path.dirname(__file__), 'database/app.db'))
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_DEFAULT_MESSAGE'] = 'Glissez-déposez vos fichiers ici<br/>ou<br/>Cliquez ici pour sélectionner vos fichiers'
app.config['DROPZONE_MAX_FILE_SIZE'] = 2048
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.pdf, .docx, .xlsx, .pptx, .txt, .jpg, .jpeg, .png, .gif'
app.config['UPLOADED_TEMP_DEST'] = os.path.normpath(os.path.join(os.path.dirname(__file__), 'static/temp'))
db = SQLAlchemy(app)
dropzone = Dropzone(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views
from app import models
from app import database
from app import requests
from app import forms
from app import nlp

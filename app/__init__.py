import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = ""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.normpath(os.path.join(os.path.dirname(__file__), 'database/app.db'))
db = SQLAlchemy(app)

from app import views
from app import models
from app import database
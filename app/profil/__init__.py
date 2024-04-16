from flask import Blueprint

bp = Blueprint('profil', __name__)

from app.profil import routes
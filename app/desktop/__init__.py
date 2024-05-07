from flask import Blueprint

bp = Blueprint("desktop", __name__)

from app.desktop import routes

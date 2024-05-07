from flask import Blueprint

bp = Blueprint("file_handler", __name__)

from app.file_handler import routes

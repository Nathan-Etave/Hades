from flask import Blueprint

bp = Blueprint('posts', __name__)

from app.api import routes

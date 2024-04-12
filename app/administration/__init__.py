from flask import Blueprint

bp = Blueprint("administration", __name__)

from app.administration import routes
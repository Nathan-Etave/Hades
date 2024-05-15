from flask import Blueprint

bp = Blueprint("password_reset", __name__)

from app.password_reset import routes
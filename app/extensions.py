from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from celery import Celery

crsf = CSRFProtect()
login_manager = LoginManager()
socketio = SocketIO()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, result_backend=Config.RESULT_BACKEND, include=['app.tasks'])
redis = FlaskRedis()
db = SQLAlchemy()
compress = Compress()
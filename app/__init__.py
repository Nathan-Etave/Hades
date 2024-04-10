from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import Config
from app.extensions import db

from app.models.a_acces import A_ACCES
from app.models.a_recherche import A_RECHERCHE
from app.models.a_tag import A_TAG
from app.models.dossier import DOSSIER
from app.models.favoris import FAVORIS
from app.models.fichier import FICHIER
from app.models.notification import NOTIFICATION
from app.models.recherche import RECHERCHE
from app.models.role import ROLE
from app.models.sous_dossier import SOUS_DOSSIER
from app.models.tag import TAG
from app.models.utilisateur import UTILISATEUR

crsf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_class = Config):
    from app.register import bp as register_bp
    from app.api import bp as api_bp
    from app.notifications import bp as notifications_bp
    from app.login import bp as login_bp

    app = Flask(__name__)
    app.config.from_object(config_class)
    crsf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager.init_app(app)
    login_manager.login_view = 'login.login'

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(register_bp, url_prefix='/inscription')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(login_bp, url_prefix='/connexion')

    return app

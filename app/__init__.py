from flask import Flask
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


def create_app(config_class = Config):
    from app.api import bp as api_bp

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

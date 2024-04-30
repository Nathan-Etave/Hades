import os
import json
from flask import Flask, current_app
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_redis import FlaskRedis
from config import Config
from celery import Celery
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
from app.utils import check_notitications, get_total_file_count, get_total_file_count_by_id
from app.models.lien import LIEN


crsf = CSRFProtect()
login_manager = LoginManager()
socketio = SocketIO()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, result_backend=Config.RESULT_BACKEND, include=['app.tasks'])
redis = FlaskRedis()

def create_app(config_class = Config, is_worker=False):
    from app.register import bp as register_bp
    from app.notifications import bp as notifications_bp
    from app.login import bp as login_bp
    from app.home import bp as home_bp
    from app.administration import bp as administration_bp
    from app.profil import bp as profil_bp
    from app.search import bp as search_bp
    from app.file_handler import bp as file_handler_bp
    from app.desktop import bp as desktop_bp

    app = Flask(__name__)
    app.config.from_object(config_class)
    crsf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        fill_db()
        if not os.path.exists(f'{current_app.root_path}/storage'):
            os.makedirs(f'{current_app.root_path}/storage')

        if not os.path.exists(f'{current_app.root_path}/storage/password'):
            os.makedirs(f'{current_app.root_path}/storage/password')
        json_file_path = f'{current_app.root_path}/storage/password/password.json'
        if not os.path.exists(json_file_path):
            with open(json_file_path, 'w') as json_file:
                json.dump({}, json_file)

    login_manager.init_app(app)
    login_manager.login_view = 'login.login'

    socketio.init_app(app)

    celery.conf.update(app.config)

    redis.init_app(app)

    if redis.get('total_files') is None:
        redis.set('total_files', 0)
    if redis.get('total_files_processed') is None:
        redis.set('total_files_processed', 0)

    if not is_worker:
        def handle_worker_status_message(message):
            data = json.loads(message['data'].decode('utf-8'))
            socketio.emit('worker_status', data, namespace='/administration')

        def handle_process_status_message(message):
            data = json.loads(message['data'].decode('utf-8'))
            total_files = data['total_files']
            total_files_processed = data['total_files_processed']
            socketio.emit('total_files', total_files, namespace='/administration')
            socketio.emit('total_files_processed', total_files_processed, namespace='/administration')

        pubsub = redis.pubsub()
        pubsub.subscribe(**{'worker_status': handle_worker_status_message})
        pubsub.subscribe(**{'process_status': handle_process_status_message})
        pubsub.run_in_thread(sleep_time=0.5)

    @app.context_processor
    def utility_processor():
        return dict(get_total_file_count=get_total_file_count,
                    get_total_file_count_by_id=get_total_file_count_by_id,
                    check_notitications=check_notitications)

    app.register_blueprint(register_bp, url_prefix='/inscription')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(login_bp, url_prefix='/connexion')
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(administration_bp, url_prefix='/administration')
    app.register_blueprint(profil_bp, url_prefix='/profil')
    app.register_blueprint(search_bp, url_prefix='/recherche')
    app.register_blueprint(file_handler_bp)
    app.register_blueprint(desktop_bp, url_prefix='/bureau')
    return app

def fill_db():
    if not ROLE.query.all():
        db.session.add(ROLE(nom_Role="ADMIN"))
        db.session.add(ROLE(nom_Role="RCH4"))
        db.session.add(ROLE(nom_Role="RCH3"))
        db.session.add(ROLE(nom_Role="RCH1/2"))
        db.session.commit()

    if not DOSSIER.query.all():
        db.session.add(DOSSIER(nom_Dossier="Décret / Circulaire", priorite_Dossier=1, couleur_Dossier="#ffffcc"))
        db.session.add(DOSSIER(nom_Dossier="GDO / GTO", priorite_Dossier=2, couleur_Dossier="#ffcc99"))
        db.session.add(DOSSIER(nom_Dossier="DTO / NDS", priorite_Dossier=3, couleur_Dossier="#ffcccc"))
        db.session.add(DOSSIER(nom_Dossier="PEX / RETEX / PIO", priorite_Dossier=4, couleur_Dossier="#ff99cc"))
        db.session.add(DOSSIER(nom_Dossier="Support formation", priorite_Dossier=5, couleur_Dossier="#ffccff"))
        db.session.add(DOSSIER(nom_Dossier="Mémoire", priorite_Dossier=6, couleur_Dossier="#cc99ff"))
        db.session.add(DOSSIER(nom_Dossier="Thèse", priorite_Dossier=7, couleur_Dossier="#ccccff"))
        db.session.add(DOSSIER(nom_Dossier="À trier", priorite_Dossier=8, couleur_Dossier="#ccffff"))
        db.session.add(DOSSIER(nom_Dossier="Archive", priorite_Dossier=9223372036854775807, couleur_Dossier="#d3d7d8"))
        db.session.commit()

    if not db.session.query(A_ACCES).all():
        for dossier in DOSSIER.query.all():
            db.session.execute(A_ACCES.insert().values(id_Role=1, id_Dossier=dossier.id_Dossier))
            db.session.execute(A_ACCES.insert().values(id_Role=2, id_Dossier=dossier.id_Dossier))
            db.session.execute(A_ACCES.insert().values(id_Role=3, id_Dossier=dossier.id_Dossier))
            db.session.execute(A_ACCES.insert().values(id_Role=4, id_Dossier=dossier.id_Dossier))
        db.session.commit()

    if not UTILISATEUR.query.all():
        db.session.add(UTILISATEUR(nom_Utilisateur="Administrateur", prenom_Utilisateur="", email_Utilisateur="admin@admin.fr", mdp_Utilisateur="$2b$12$sOih7qRKimxwqJXITajOfO.Twyg.lModCMYSrgxLpxGompCQjjM56", telephone_Utilisateur="", est_Actif_Utilisateur=True, id_Role=1))
        # password: O]SxR=rBv%
        db.session.commit()
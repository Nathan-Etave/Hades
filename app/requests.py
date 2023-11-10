from app import db
from app.models import CATEGORIE, POMPIER, table_SOUS_CATEGORIE, table_FAVORI, FICHIER, ANOTIFICATION, SIGNALEMENT, NOTIFICATION, DATE
from sqlalchemy.orm import sessionmaker
from datetime import datetime

def get_root_categories():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_categories = CATEGORIE.query.all()
    root_categories = []
    while all_categories:
        category = all_categories.pop(0)
        if not session.query(table_SOUS_CATEGORIE).filter_by(categorieEnfant=category.idCategorie).all():
            root_categories.append(category)
    return root_categories

def get_user_favourites_file(idUser):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_favourites = session.query(table_FAVORI).filter_by(idPompier=idUser).all()
    favourites = []
    while all_favourites:
        favourite = all_favourites.pop(0)
        favourites.append(session.query(FICHIER).filter_by(idFichier=favourite.idFichier).first())
    return favourites

def get_user_by_id(id):
    return POMPIER.query.filter_by(idPompier=id).first()

def get_user_by_email(email):
    return POMPIER.query.filter_by(emailPompier=email).first()

def get_file_by_id(id):
    return FICHIER.query.filter_by(idFichier=id).first()

def user_has_notifications(idUser):
    return ANOTIFICATION.query.filter_by(idPompier=idUser).first() is not None

def add_to_user_favourites(idUser, idFile):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.insert().values(idFichier=idFile, idPompier=idUser))
    session.commit()

def remove_from_user_favourites(idUser, idFile):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.delete().where(table_FAVORI.c.idFichier == idFile).where(table_FAVORI.c.idPompier == idUser))
    session.commit()

def add_administrator_signalement(idFile, idUser, description):
    db.session.add(SIGNALEMENT(idFichier=idFile, idPompier=idUser, descriptionSignalement=description))
    db.session.commit()
    file = FICHIER.query.filter_by(idFichier=idFile).first()
    all_administrators = POMPIER.query.filter_by(idRole=1).all()
    while all_administrators:
        administrator = all_administrators.pop(0)
        db.session.add(NOTIFICATION(texteNotification=f'Un signalement a été fait sur le fichier {file.nomFichier} ({file.idFichier})', typeChange='signalement', raisonNotification=description))
        db.session.add(DATE(laDate=datetime.now()))
        db.session.commit()
        db.session.add(ANOTIFICATION(idPompier=administrator.idPompier, idNotification=NOTIFICATION.query.order_by(NOTIFICATION.idNotification.desc()).first().idNotification, idFichier=file.idFichier, idDate=DATE.query.order_by(DATE.idDate.desc()).first().idDate))
        db.session.commit()
    return True
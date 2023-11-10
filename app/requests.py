from app import db
from app.models import CATEGORIE, POMPIER, table_SOUS_CATEGORIE, table_FAVORI, FICHIER, ANOTIFICATION, SIGNALEMENT, NOTIFICATION, DATE, ACONSULTE, TAG, table_A_TAG
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from unidecode import unidecode

def get_root_categories():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_categories = CATEGORIE.query.all()
    root_categories = []
    while all_categories:
        category = all_categories.pop(0)
        if not session.query(table_SOUS_CATEGORIE).filter_by(categorieEnfant=category.idCategorie).all():
            root_categories.append(category)
    session.close()
    return root_categories

def get_user_favourites_file(id_user):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_favourites = session.query(table_FAVORI).filter_by(idPompier=id_user).all()
    favourites = []
    while all_favourites:
        favourite = all_favourites.pop(0)
        favourites.append(session.query(FICHIER).filter_by(idFichier=favourite.idFichier).first())
    session.close()
    return favourites

def get_user_by_id(id):
    return POMPIER.query.filter_by(idPompier=id).first()

def get_user_by_email(email):
    return POMPIER.query.filter_by(emailPompier=email).first()

def get_file_by_id(id):
    return FICHIER.query.filter_by(idFichier=id).first()

def user_has_notifications(id_user):
    return ANOTIFICATION.query.filter_by(idPompier=id_user).first() is not None

def add_to_user_favourites(id_user, idFile):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.insert().values(idFichier=idFile, idPompier=id_user))
    session.close()
    session.commit()

def remove_from_user_favourites(id_user, idFile):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.delete().where(table_FAVORI.c.idFichier == idFile).where(table_FAVORI.c.idPompier == id_user))
    session.close()
    session.commit()

def add_administrator_signalement(id_file, id_user, description):
    db.session.add(SIGNALEMENT(idFichier=id_file, idPompier=id_user, descriptionSignalement=description))
    db.session.commit()
    file = FICHIER.query.filter_by(idFichier=idFile).first()
    all_administrators = POMPIER.query.filter_by(idRole=1).all()
    while all_administrators:
        administrator = all_administrators.pop(0)
        db.session.add(NOTIFICATION(texteNotification=f'Un signalement a été fait sur le fichier {file.nomFichier} ({file.idFichier})', typeChange='Signalement', raisonNotification=description))
        db.session.add(DATE(laDate=datetime.now()))
        db.session.commit()
        db.session.add(ANOTIFICATION(idPompier=administrator.idPompier, idNotification=NOTIFICATION.query.order_by(NOTIFICATION.idNotification.desc()).first().idNotification, idFichier=file.idFichier, idDate=DATE.query.order_by(DATE.idDate.desc()).first().idDate))
        db.session.commit()

def get_user_notifications(id_user):
    all_notifications = (ANOTIFICATION).query.filter_by(idPompier=id_user).all()
    notifications = []
    while all_notifications:
        notification = all_notifications.pop(0)
        notifications.append((NOTIFICATION.query.filter_by(idNotification=notification.idNotification).first(), FICHIER.query.filter_by(idFichier=notification.idFichier).first(), DATE.query.filter_by(idDate=notification.idDate).first()))
    return notifications

def remove_from_user_notification(id_notification, id_fichier, idd_date, id_user):
    db.session.delete(ANOTIFICATION.query.filter_by(idPompier=id_user).filter_by(idNotification=id_notification).filter_by(idFichier=id_fichier).filter_by(idDate=idd_date).first())
    db.session.commit()

def get_file_order_by_date(id_user):
    all_file = ACONSULTE.query.filter_by(idPompier=id_user).join(DATE).order_by(DATE.laDate).all()
    files = []
    while all_file :
        file = all_file.pop(0)
        files.append(FICHIER.query.filter_by(idFichier=file.idFichier).first())
    return files

def update_user(id_user, prenom, nom, mail, telephone, mdp):
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.prenomPompier = prenom
    user.nomPompier = nom
    user.emailPompier = mail
    user.telephonePompier = telephone
    user.mdpPompier = mdp
    db.session.commit()

def update_user_photo(id_user, photo):
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.photoPompier = photo
    db.session.commit()
    
def get_file_by_tag(search_term):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    search_term = unidecode(search_term.lower())
    search_term_list = search_term.split(' ')
    all_tags = []
    while search_term_list:
        term = search_term_list.pop(0)
        tag = TAG.query.filter_by(nomTag=term).first()
        if tag and tag not in all_tags:
            all_tags.append(tag)
    files = []
    while all_tags:
        tag = all_tags.pop(0)
        all_files = session.query(table_A_TAG).filter_by(nomTag=tag.nomTag).all()
        while all_files:
            file = all_files.pop(0)
            files.append(FICHIER.query.filter_by(idFichier=file.idFichier).first())
    session.close()
    return files

def get_all_files():
    return FICHIER.query.all()
from app import db
from app.models import (CATEGORIE, POMPIER, table_SOUS_CATEGORIE, table_FAVORI, FICHIER, ANOTIFICATION,
                        SIGNALEMENT, NOTIFICATION, DATE, ACONSULTE, TAG, table_A_TAG, table_EST_CATEGORIE,
                        table_HISTORIQUE)
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

def add_to_user_favourites(id_user, id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.insert().values(idFichier=id_file, idPompier=id_user))
    session.commit()
    session.close()

def remove_from_user_favourites(id_user, id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.delete().where(table_FAVORI.c.idFichier == id_file).where(table_FAVORI.c.idPompier == id_user))
    session.commit()
    session.close()

def add_administrator_signalement(id_file, id_user, description):
    all_administrators = POMPIER.query.filter_by(idRole=1).all()
    date = DATE(laDate=datetime.now())
    db.session.add(date)
    db.session.commit()
    file = FICHIER.query.filter_by(idFichier=id_file).first()
    notification = NOTIFICATION(texteNotification=f'Un signalement a été fait sur le fichier {file.nomFichier} ({file.idFichier})', typeChange='Signalement', raisonNotification=description)
    db.session.add(notification)
    db.session.commit()
    db.session.add(SIGNALEMENT(idFichier=id_file, idPompier=id_user, idDate=date.idDate, descriptionSignalement=description))
    db.session.commit()
    while all_administrators:
        administrator = all_administrators.pop(0)
        db.session.add(ANOTIFICATION(idPompier=administrator.idPompier, idNotification=notification.idNotification, idFichier=file.idFichier, idDate=date.idDate))
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
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_file = session.query(ACONSULTE).filter_by(idPompier=id_user).join(DATE).order_by(DATE.laDate).all()
    files = []
    while all_file :
        file = all_file.pop(0)
        files.append(session.query(FICHIER).filter_by(idFichier=file.idFichier).first())
    session.close()
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

def get_file_history(id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    history = []
    while session.query(table_HISTORIQUE).filter_by(nouvelleVersion=id_file).first() is not None:
        id_file = session.query(table_HISTORIQUE).filter_by(nouvelleVersion=id_file).first().ancienneVersion
        history.append(FICHIER.query.filter_by(idFichier=id_file).first())
    session.close()
    return history

def get_file_by_categorie_unique(id_categorie):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_files = session.query(table_EST_CATEGORIE).filter_by(idCategorie=id_categorie).all()
    files = []
    while all_files:
        file = all_files.pop(0)
        files.append(session.query(FICHIER).filter_by(idFichier=file.idFichier).first())
    session.close()
    return set(files)

def get_liste_sous_categorie(id_categorie) :
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_sous_categories = session.query(table_SOUS_CATEGORIE).filter_by(categorieParent=id_categorie).all()
    sous_categories = set()
    while all_sous_categories:
        sous_categorie = all_sous_categories.pop(0)
        sous_categories.add(session.query(CATEGORIE).filter_by(idCategorie=sous_categorie.categorieEnfant).first())
    session.close()
    for sous_categorie in sous_categories:
        sous_categories = sous_categories | get_liste_sous_categorie(sous_categorie.idCategorie)
    return sous_categories

def get_file_by_categorie(id_categorie) :
    res = set()
    res = res | get_file_by_categorie_unique(id_categorie)
    sous_categories = get_liste_sous_categorie(id_categorie)
    for id_cat in sous_categories:
        res = res | get_file_by_categorie_unique(id_cat.idCategorie)
    return list(res)

def get_file_tags(id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_tags = session.query(table_A_TAG).filter_by(idFichier=id_file).all()
    tags = []
    while all_tags:
        tag = all_tags.pop(0)
        tags.append(TAG.query.filter_by(nomTag=tag.nomTag).first())
    session.close()
    return tags

def get_category_tree(category_id=None):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    if category_id is None:
        categories = session.query(CATEGORIE).filter(CATEGORIE.idCategorie.notin_(
            session.query(table_SOUS_CATEGORIE.c.categorieEnfant))).all()
    else:
        subcategories = session.query(CATEGORIE).filter(CATEGORIE.idCategorie.in_(
            session.query(table_SOUS_CATEGORIE.c.categorieEnfant).filter_by(categorieParent=category_id))).all()
        categories = subcategories
    session.close()
    category_tree = []
    for category in categories:
        subcategories = get_liste_sous_categorie(category.idCategorie)
        if subcategories:
            subcategory_tree = get_category_tree(category.idCategorie)
        else:
            subcategory_tree = []
        category_tree.append([category, subcategory_tree])
    return category_tree

def add_file_to_database(file, filename, extension, tags, categories, id_etat):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    file = FICHIER(nomFichier=filename, data=file, extensionFichier=extension, idEtatFichier=id_etat)
    session.add(file)
    session.commit()
    for tag in tags:
        is_tag_exists = session.query(TAG.nomTag).filter_by(nomTag=tag).first() is not None
        if not is_tag_exists:
            new_tag = TAG(nomTag=tag)
            session.add(new_tag)
            session.commit()
        session.execute(table_A_TAG.insert().values(nomTag=tag, idFichier=file.idFichier))
    for categorie in categories:
        session.execute(table_EST_CATEGORIE.insert().values(idCategorie=categorie, idFichier=file.idFichier))
    session.commit()
    session.close()

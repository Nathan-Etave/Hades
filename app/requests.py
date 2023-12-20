from app import db
from app.models import (CATEGORIE, POMPIER, table_SOUS_CATEGORIE, table_FAVORI, FICHIER, ANOTIFICATION,
                        SIGNALEMENT, NOTIFICATION, DATE, ACONSULTE, TAG, table_A_TAG, table_EST_CATEGORIE,
                        table_A_ACCES, ROLEPOMPIER, table_HISTORIQUE)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import asc
from datetime import datetime
from unidecode import unidecode
from pytz import timezone

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

def add_user( prenom, nom, email, telephone,role, mdp):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    id = POMPIER.query.count() + 1
    user = POMPIER(idPompier=id, nomPompier = nom,prenomPompier = prenom, emailPompier = email, telephonePompier = telephone,
                   mdpPompier = mdp,photoPompier = bytes("","utf-8"),idRole = role)
    session.add(user)
    session.commit()
    session.close()
    
def desactivate_user(id_user):
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.idRole = 2
    db.session.commit()
    
def get_role_by_id(id):
    return ROLEPOMPIER.query.filter_by(idRole=id).first()

def get_role_pompier():
    pompiers = POMPIER.query.all() 
    role_dict = {}
    for pompier in pompiers:
        nomrole = get_role_by_id(pompier.idRole)
        if nomrole not in role_dict:
            role_dict[nomrole] = []
        role_dict[nomrole].append(pompier)
    return role_dict

def get_user_by_id(id):
    return POMPIER.query.filter_by(idPompier=id).first()

def get_user_by_email(email):
    return POMPIER.query.filter_by(emailPompier=email).first()

def get_user_by_nom(nom, prenom):
    return POMPIER.query.filter_by(nomPompier=nom, prenomPompier=prenom).first()

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
    date = DATE(laDate=datetime.now(timezone('Europe/Paris')))
    db.session.add(date)
    db.session.commit()
    file = FICHIER.query.filter_by(idFichier=id_file).first()
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    notification = NOTIFICATION(texteNotification=f'{user.prenomPompier} {user.nomPompier} a signalé le fichier {file.nomFichier} ({file.idFichier})', typeChange='Signalement', raisonNotification=description)
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

def update_user(id_user, prenom, nom, mail, telephone, mdp,role=None):
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.prenomPompier = prenom
    user.nomPompier = nom
    user.emailPompier = mail
    user.telephonePompier = telephone
    user.mdpPompier = mdp
    if role is not None:
        user.idRole = role
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

def get_file_category_leaves(id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_categories = session.query(table_EST_CATEGORIE).filter_by(idFichier=id_file).all()
    categories = []
    while all_categories:
        category = all_categories.pop(0)
        categories.append(session.query(CATEGORIE).filter_by(idCategorie=category.idCategorie).first())
    session.close()
    return categories

def update_old_file(file, filename, extension, tags, categories, id_etat, old_file_id):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    old_file = session.query(FICHIER).filter_by(idFichier=old_file_id).first()
    old_file.idEtatFichier = 1
    session.commit()
    new_file = FICHIER(nomFichier=filename, data=file, extensionFichier=extension, idEtatFichier=id_etat)
    session.add(new_file)
    session.commit()
    new_id = new_file.idFichier
    session.execute(table_HISTORIQUE.insert().values(ancienneVersion=old_file.idFichier, nouvelleVersion=new_file.idFichier))
    for tag in tags:
        is_tag_exists = session.query(TAG.nomTag).filter_by(nomTag=tag).first() is not None
        if not is_tag_exists:
            new_tag = TAG(nomTag=tag)
            session.add(new_tag)
            session.commit()
        session.execute(table_A_TAG.insert().values(nomTag=tag, idFichier=new_file.idFichier))
    for categorie in categories:
        session.execute(table_EST_CATEGORIE.insert().values(idCategorie=categorie, idFichier=new_file.idFichier))
    session.commit()
    session.close()
    return new_id

def remove_file(id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    old_versions = session.query(table_HISTORIQUE).filter_by(ancienneVersion=id_file).all()
    id_old_versions = [old_file[1] for old_file in old_versions]
    session.query(table_A_TAG).filter_by(idFichier=id_file).delete()
    session.query(table_EST_CATEGORIE).filter_by(idFichier=id_file).delete()
    session.query(table_FAVORI).filter_by(idFichier=id_file).delete()
    session.query(table_HISTORIQUE).filter_by(ancienneVersion=id_file).delete()
    session.query(ANOTIFICATION).filter_by(idFichier=id_file).delete()
    session.query(SIGNALEMENT).filter_by(idFichier=id_file).delete()
    session.query(ACONSULTE).filter_by(idFichier=id_file).delete()
    session.query(FICHIER).filter_by(idFichier=id_file).delete()
    session.commit()
    for id_old_version in id_old_versions:
        remove_file(id_old_version)
    session.close()

def update_file_tags(id_file, tags):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.query(table_A_TAG).filter_by(idFichier=id_file).delete()
    session.commit()
    for tag in tags:
        is_tag_exists = session.query(TAG.nomTag).filter_by(nomTag=tag).first() is not None
        if not is_tag_exists:
            new_tag = TAG(nomTag=tag)
            session.add(new_tag)
            session.commit()
        session.execute(table_A_TAG.insert().values(nomTag=tag, idFichier=id_file))
    session.commit()
    session.close()

def update_file_categories(id_file, categories):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.query(table_EST_CATEGORIE).filter_by(idFichier=id_file).delete()
    session.commit()
    for categorie in categories:
        session.execute(table_EST_CATEGORIE.insert().values(idCategorie=categorie, idFichier=id_file))
    session.commit()
    session.close()

def add_consulted_file(id_user, id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    date = DATE(laDate=datetime.now())
    session.add(date)
    session.commit()
    session.add(ACONSULTE(idPompier=id_user, idFichier=id_file, idDate=date.idDate))
    session.commit()
    session.close()
    
def get_category_file(id_file):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_categories = session.query(table_EST_CATEGORIE).filter_by(idFichier=id_file).all()
    categories = []
    while all_categories:
        categorie = all_categories.pop(0)
        categories.append(session.query(CATEGORIE).filter_by(idCategorie=categorie.idCategorie).first())
    session.close()
    return categories

def is_valide_file(user_id, file_id) :
    Session = sessionmaker(bind=db.engine)
    session = Session()
    id_etat = session.query(FICHIER.idEtatFichier).filter_by(idFichier=file_id).first()[0]
    if id_etat != 2 :
        return False
    lst_category = get_category_file(file_id)
    id_role = session.query(POMPIER.idRole).filter_by(idPompier=user_id).first()[0]
    for category in lst_category :
        lst_access = []
        for row in session.query(table_A_ACCES.c.idRole).filter_by(idCategorie=category.idCategorie).all() :
            lst_access.append(row[0])
        if id_role not in lst_access :
            return False
    return True

def remove_forbiden_file(file_list, user_id) :
    res = []
    for file in file_list :
        if is_valide_file(user_id, file.idFichier) :
            res.append(file)
    return res

def get_file_by_consult(id_user):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_files = session.query(ACONSULTE).filter_by(idPompier=id_user).order_by(asc(ACONSULTE.dateConsultation)).all()
    files = []
    for file in all_files:
        files.append(session.query(FICHIER).filter_by(idFichier=file.idFichier).first())
    session.close()
    return files

def get_file_by_extension(extension):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    files = session.query(FICHIER).filter_by(extensionFichier=extension).all()
    session.close()
    return files

def get_all_extension():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    extensions = session.query(FICHIER.extensionFichier).distinct().all()
    extensions_set = set()
    while extensions:
        extension = extensions.pop(0)[0]
        extensions_set.add(extension)
    session.close()
    return list(extensions_set)

def add_category_to_database(name, parent_id):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    category = CATEGORIE(nomCategorie=name)
    session.add(category)
    session.commit()
    if parent_id is not None:
        session.execute(table_SOUS_CATEGORIE.insert().values(categorieParent=parent_id, categorieEnfant=category.idCategorie))
    session.commit()
    session.close()

def update_category_from_database(category_id, name):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    category = session.query(CATEGORIE).filter_by(idCategorie=category_id).first()
    category.nomCategorie = name
    session.commit()
    session.close()

def remove_category_from_database(category_id):
    sous_categories = get_liste_sous_categorie(category_id)
    Session = sessionmaker(bind=db.engine)
    session = Session()
    for sous_categorie in sous_categories:
        remove_category_from_database(sous_categorie.idCategorie)
    files = session.query(table_EST_CATEGORIE).filter_by(idCategorie=category_id).all()
    for file in files:
        other_categories = session.query(table_EST_CATEGORIE).filter(table_EST_CATEGORIE.c.idFichier == file.idFichier, table_EST_CATEGORIE.c.idCategorie != category_id).all()
        if len(other_categories) == 0:
            session.query(table_EST_CATEGORIE).filter(table_EST_CATEGORIE.c.idFichier == file.idFichier, table_EST_CATEGORIE.c.idCategorie == category_id).update({table_EST_CATEGORIE.c.idCategorie: 1}, synchronize_session=False)
    session.query(table_SOUS_CATEGORIE).filter_by(categorieParent=category_id).delete()
    session.query(table_SOUS_CATEGORIE).filter_by(categorieEnfant=category_id).delete()
    session.query(CATEGORIE).filter_by(idCategorie=category_id).delete()
    session.commit()
    session.close()

def get_all_roles():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    extensions = session.query(ROLEPOMPIER.idRole,ROLEPOMPIER.nomRole).distinct().all()
    extensions_set = set()
    while extensions:
        extension = extensions.pop(0)
        extensions_set.add(str(extension[0])+" "+extension[1])
    session.close()
    return list(extensions_set)
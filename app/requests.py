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
    """ fonction qui retourne les catégories racines

    Returns:
        List : liste des catégories racines
    """    
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
    """
    Récupère les fichiers favoris d'un utilisateur.

    Args:
        id_user (int): L'ID de l'utilisateur.

    Returns:
        list: Une liste de fichiers favoris associés à l'utilisateur.
    """
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
    """
    Ajoute un utilisateur à la base de données.

    Args:
        prenom (str): Le prénom de l'utilisateur.
        nom (str): Le nom de l'utilisateur.
        email (str): L'adresse e-mail de l'utilisateur.
        telephone (str): Le numéro de téléphone de l'utilisateur.
        role (int): L'identifiant du rôle de l'utilisateur.
        mdp (str): Le mot de passe de l'utilisateur.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    id = POMPIER.query.count() + 1
    user = POMPIER(idPompier=id, nomPompier = nom,prenomPompier = prenom, emailPompier = email, telephonePompier = telephone,
                   mdpPompier = mdp,photoPompier = bytes("","utf-8"),idRole = role)
    session.add(user)
    session.commit()
    session.close()
    
def desactivate_user(id_user):
    """
    Désactive un utilisateur en définissant son ID de rôle à 2.
    
    Args:
        id_user (int): L'ID de l'utilisateur à désactiver.
    
    Returns:
        None
    """
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.idRole = 2
    db.session.commit()
    
def get_role_by_id(id):
    """
    Récupère un rôle par son ID.

    Args:
        id (int): L'ID du rôle à récupérer.

    Returns:
        dict: Un dictionnaire contenant les informations du rôle.
    """
    return ROLEPOMPIER.query.filter_by(idRole=id).first()

def get_role_pompier(): 
    """
    Récupère le rôle de chaque pompier.

    Returns:
        dict: Un dictionnaire où les clés sont les noms des rôles et les valeurs sont des listes de pompiers ayant ce rôle.
    """
    role_dict = {}
    for role in ROLEPOMPIER.query.all():
        role_dict[role] = []
    pompiers = POMPIER.query.all() 
    for pompier in pompiers:
        role_dict[get_role_by_id(pompier.idRole)].append(pompier)
    return role_dict

def get_user_by_id(id):
    """
    Récupère un utilisateur par son ID.

    Args:
        id (int): L'ID de l'utilisateur à récupérer.

    Returns:
        dict: Un dictionnaire contenant les informations de l'utilisateur.
    """
    return POMPIER.query.filter_by(idPompier=id).first()

def get_user_by_email(email):
    """
    Récupère un utilisateur en fonction de son adresse e-mail.

    Args:
        email (str): L'adresse e-mail de l'utilisateur.

    Returns:
        dict: Un dictionnaire contenant les informations de l'utilisateur.
    """
    return POMPIER.query.filter_by(emailPompier=email).first()

def get_user_by_name(nom, prenom):
    return POMPIER.query.filter_by(nomPompier=nom, prenomPompier=prenom).first()

def get_file_by_id(id):
    """
    Récupère un fichier par son ID.

    Args:
        id (int): L'ID du fichier à récupérer.

    Returns:
        dict: Un dictionnaire contenant les informations du fichier.
    """
    return FICHIER.query.filter_by(idFichier=id).first()

def user_has_notifications(id_user):
    """
    Vérifie si un utilisateur a des notifications.

    Args:
        id_user (int): L'identifiant de l'utilisateur.

    Returns:
        bool: True si l'utilisateur a des notifications, False sinon.
    """
    return ANOTIFICATION.query.filter_by(idPompier=id_user).first() is not None

def add_to_user_favourites(id_user, id_file):
    """
    Ajoute un fichier aux favoris d'un utilisateur.

    Paramètres:
        id_user (int): L'ID de l'utilisateur.
        id_file (int): L'ID du fichier.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.insert().values(idFichier=id_file, idPompier=id_user))
    session.commit()
    session.close()

def remove_from_user_favourites(id_user, id_file):
    """
    Supprime un fichier des favoris d'un utilisateur.

    Paramètres:
        id_user (int): L'ID de l'utilisateur.
        id_file (int): L'ID du fichier à supprimer.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.execute(table_FAVORI.delete().where(table_FAVORI.c.idFichier == id_file).where(table_FAVORI.c.idPompier == id_user))
    session.commit()
    session.close()

def add_administrator_signalement(id_file, id_user, description):
    """
    Ajoute un signalement pour un fichier par un administrateur.

    Args:
        id_file (int): L'ID du fichier.
        id_user (int): L'ID de l'utilisateur qui a signalé le fichier.
        description (str): La description du signalement.

    Returns:
        None
    """
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
    """
    Récupère les notifications pour un utilisateur donné.

    Args:
        id_user (int): L'ID de l'utilisateur.

    Returns:
        list: Une liste de notifications.
    """
    all_notifications = (ANOTIFICATION).query.filter_by(idPompier=id_user).all()
    notifications = []
    while all_notifications:
        notification = all_notifications.pop(0)
        notifications.append((NOTIFICATION.query.filter_by(idNotification=notification.idNotification).first(), FICHIER.query.filter_by(idFichier=notification.idFichier).first(), DATE.query.filter_by(idDate=notification.idDate).first()))
    return notifications

def remove_from_user_notification(id_notification, id_fichier, idd_date, id_user):
    """
    Supprime une notification d'un utilisateur.

    Parameters:
    - id_notification (int): L'ID de la notification.
    - id_fichier (int): L'ID du fichier associé à la notification.
    - idd_date (int): L'ID de la date associée à la notification.
    - id_user (int): L'ID de l'utilisateur.

    Returns:
    None
    """
    db.session.delete(ANOTIFICATION.query.filter_by(idPompier=id_user).filter_by(idNotification=id_notification).filter_by(idFichier=id_fichier).filter_by(idDate=idd_date).first())
    db.session.commit()

def get_file_order_by_date(id_user):
    """
    Récupère les fichiers associés à un utilisateur, triés par date.

    Args:
        id_user (int): L'ID de l'utilisateur.

    Returns:
        list: Une liste de fichiers associés à l'utilisateur, triés par date.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_file = session.query(ACONSULTE).filter_by(idPompier=id_user).join(DATE).order_by(DATE.laDate).all()
    files = []
    while all_file :
        file = all_file.pop(0)
        files.append(session.query(FICHIER).filter_by(idFichier=file.idFichier).first())
    session.close()
    return files

def update_user(id_user, prenom, nom, mail, telephone, mdp=None, role=None):
    """
    Met à jour les informations de l'utilisateur dans la base de données.

    Args:
        id_user (int): L'ID de l'utilisateur à mettre à jour.
        prenom (str): Le prénom mis à jour de l'utilisateur.
        nom (str): Le nom de famille mis à jour de l'utilisateur.
        mail (str): L'adresse e-mail mise à jour de l'utilisateur.
        telephone (str): Le numéro de téléphone mis à jour de l'utilisateur.
        mdp (str, optionnel): Le mot de passe mis à jour de l'utilisateur. Par défaut, None.
        role (int, optionnel): L'ID du rôle mis à jour de l'utilisateur. Par défaut, None.
    """
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.prenomPompier = prenom
    user.nomPompier = nom
    user.emailPompier = mail
    user.telephonePompier = telephone
    if mdp is not None:
        user.mdpPompier = mdp
    if role is not None:
        user.idRole = role
    db.session.commit()

def update_user_photo(id_user, photo):
    """
    Met à jour la photo d'un utilisateur identifié par son ID.

    Args:
        id_user (int): L'ID de l'utilisateur à mettre à jour.
        photo (): La photo de l'utilisateur.

    Returns:
        None
    """
    user = POMPIER.query.filter_by(idPompier=id_user).first()
    user.photoPompier = photo
    db.session.commit()
    
def get_file_by_tag(search_term):
    """
    Récupère les fichiers en fonction d'un terme de recherche donné.

    Args:
        search_term (str): Le terme de recherche pour filtrer les fichiers par tag.

    Returns:
        list: Une liste de fichiers correspondant au terme de recherche.
    """
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
    """
    Récupère tous les fichiers de la base de données.
    
    Returns:
        list: Une liste de tous les fichiers de la base de données.
    """
    return FICHIER.query.all()

def get_file_history(id_file):
    """
    Récupère l'historique d'un fichier en fonction de son ID.

    Args:
        id_file (int): L'ID du fichier.

    Returns:
        list: Une liste de fichier représentant l'historique du fichier.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    history = []
    while session.query(table_HISTORIQUE).filter_by(nouvelleVersion=id_file).first() is not None:
        id_file = session.query(table_HISTORIQUE).filter_by(nouvelleVersion=id_file).first().ancienneVersion
        history.append(FICHIER.query.filter_by(idFichier=id_file).first())
    session.close()
    return history

def get_file_by_categorie_unique(id_categorie):
    """
    Récupère les fichiers directement associés à une catégorie.

    Args:
        id_categorie (int): L'ID de la catégorie.

    Returns:
        set: Un ensemble de fichiers associés à l'ID de catégorie donné.
    """
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
    """
    Récupère un ensemble de sous-catégories de manière récursive en fonction de l'ID de la catégorie donnée.

    Paramètres:
        id_categorie (int): L'ID de la catégorie parente.

    Retour:
        set: Un ensemble de sous-catégories.
    """
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
    """
    Récupère une liste de fichiers en fonction de l'ID de la catégorie donnée.

    Args:
        id_categorie (int): L'ID de la catégorie.

    Returns:
        [List]: Une liste de fichiers correspondant à la catégorie donnée.
    """
    res = set()
    res = res | get_file_by_categorie_unique(id_categorie)
    sous_categories = get_liste_sous_categorie(id_categorie)
    for id_cat in sous_categories:
        res = res | get_file_by_categorie_unique(id_cat.idCategorie)
    return list(res)

def get_file_tags(id_file):
    """
    Récupère les tags associés à un fichier.

    Args:
        id_file (int): L'ID du fichier.

    Returns:
        list: Une liste de tags associés au fichier.
    """
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
    """
    Récupère l'arborescence des catégories à partir de l'ID de catégorie donné.
    Si aucun ID de catégorie n'est fourni, récupère l'ensemble de l'arborescence des catégories.

    Args:
        category_id (int, optionnel): L'ID de la catégorie à partir de laquelle commencer l'arborescence. Par défaut, None.

    Returns:
        list: Une liste imbriquée représentant l'arborescence des catégories. Chaque élément de la liste est une paire contenant
        l'objet catégorie et le nombre de fichiers associés à cette catégorie. Le deuxième élément de
        chaque paire est une liste représentant l'arborescence des sous-catégories.

    """
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
        a = get_file_by_categorie(category.idCategorie)
        new_l = []
        seen_ids = set()
        for d in a:
            if d.idFichier not in seen_ids and d.idEtatFichier == 2:
                seen_ids.add(d.idFichier)
                new_l.append(d)
        category_tree.append([[category, len(new_l)], subcategory_tree])
    return category_tree

def add_file_to_database(file, filename, extension, tags, categories, id_etat):
    """
    Ajoute un fichier à la base de données avec les informations fournies.

    Args:
        file (bytes): Les données du fichier.
        filename (str): Le nom du fichier.
        extension (str): L'extension du fichier.
        tags (list): Une liste de tags associés au fichier.
        categories (list): Une liste de catégories associées au fichier.
        id_etat (int): L'ID de l'état du fichier.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    file = FICHIER(nomFichier=filename, data=file, extensionFichier=extension, idEtatFichier=id_etat)
    session.add(file)
    session.commit()
    for tag in tags:
        tag = unidecode(tag.lower())
        existing_tag = session.query(TAG).filter_by(nomTag=tag).first()
        if existing_tag is None:
            new_tag = TAG(nomTag=tag)
            session.add(new_tag)
            session.commit()
        existing_association = session.query(table_A_TAG).filter_by(nomTag=tag, idFichier=file.idFichier).first()
        if existing_association is None:
            session.execute(table_A_TAG.insert().values(nomTag=tag, idFichier=file.idFichier))
    if categories == []:
        categories = [1]
    for categorie in categories:
        session.execute(table_EST_CATEGORIE.insert().values(idCategorie=categorie, idFichier=file.idFichier))
    session.commit()
    session.close()

def get_file_category_leaves(id_file):
    """
    Récupère les categories associées à un fichier.

    Paramètres:
    id_file (int): L'ID du fichier.

    Retourne:
    list: Une liste de catégorie associées au fichier.
    """
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
    """
    Met à jour un ancien fichier avec de nouvelles informations et l'enregistre dans la base de données.

    Args:
        file (bytes): Les données du fichier.
        filename (str): Le nom du fichier.
        extension (str): L'extension du fichier.
        tags (list): Liste des tags associés au fichier.
        categories (list): Liste des catégories associées au fichier.
        id_etat (int): L'ID de l'état du fichier.
        old_file_id (int): L'ID de l'ancien fichier à mettre à jour.

    Returns:
        int: L'ID du fichier récemment mis à jour.
    """
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
        tag = unidecode(tag.lower())
        is_tag_exists = session.query(TAG.nomTag).filter_by(nomTag=tag).first() is not None
        if not is_tag_exists:
            new_tag = TAG(nomTag=tag)
            session.add(new_tag)
            session.commit()
        session.execute(table_A_TAG.insert().values(nomTag=tag, idFichier=new_file.idFichier))
    if categories == []:
        categories = [1]
    for categorie in categories:
        session.execute(table_EST_CATEGORIE.insert().values(idCategorie=categorie, idFichier=new_file.idFichier))
    session.commit()
    session.close()
    return new_id

def remove_file(id_file):
    """
    Supprime un fichier et ses données associées de la base de données.

    Args:
        id_file (int): L'ID du fichier à supprimer.

    Returns:
        None
    """
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
    """
    Met à jour les tags d'un fichier dans la base de données.

    Args:
        id_file (int): L'ID du fichier.
        tags (list): La liste des tags à mettre à jour.

    Returns:
        None
    """

    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.query(table_A_TAG).filter_by(idFichier=id_file).delete()
    session.commit()
    for tag in tags:
        tag = unidecode(tag.lower())
        is_tag_exists = session.query(TAG.nomTag).filter_by(nomTag=tag).first() is not None
        if not is_tag_exists:
            new_tag = TAG(nomTag=tag)
            session.add(new_tag)
            session.commit()
        session.execute(table_A_TAG.insert().values(nomTag=tag, idFichier=id_file))
    session.commit()
    session.close()

def update_file_categories(id_file, categories):
    """
    Met à jour les catégories d'un fichier dans la base de données.

    Paramètres:
        id_file (int): L'ID du fichier à mettre à jour.
        categories (list): La liste des IDs de catégories à assigner au fichier.

    Retour:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.query(table_EST_CATEGORIE).filter_by(idFichier=id_file).delete()
    session.commit()
    for categorie in categories:
        session.execute(table_EST_CATEGORIE.insert().values(idCategorie=categorie, idFichier=id_file))
    session.commit()
    session.close()

def add_consulted_file(id_user, id_file):
    """
    Ajoute la consultation d'un fichier à la base de données.

    Paramètres:
        id_user (int): L'ID de l'utilisateur qui a consulté le fichier.
        id_file (int): L'ID du fichier qui a été consulté.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    date = DATE(laDate=datetime.now())
    session.add(date)
    session.commit()
    session.add(ACONSULTE(idPompier=id_user, idFichier=id_file, idDate=date.idDate))
    session.commit()
    session.close()
    
def get_category_file(id_file):
    """
    Récupère les catégories associées à un ID de fichier donné.

    Args:
        id_file (int): L'ID du fichier.

    Returns:
        list: Une liste de catégorie associés au fichier.
    """
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
    """
    Vérifie si un fichier est valide pour un utilisateur donné.

    Args:
        user_id (int): L'ID de l'utilisateur.
        file_id (int): L'ID du fichier.

    Returns:
        bool: True si le fichier est valide pour l'utilisateur, False sinon.
    """
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
            session.close()
            return False
    session.close()
    return True

def remove_forbiden_file(file_list, user_id) :
    """
    Supprime les fichiers interdits de la liste de fichiers donnée en fonction de l'ID de l'utilisateur.

    Args:
        file_list (list): Liste des fichiers à vérifier.
        user_id (int): ID de l'utilisateur.

    Returns:
        list: Liste des fichiers valides pour l'utilisateur.
    """
    res = []
    for file in file_list :
        if is_valide_file(user_id, file.idFichier) :
            res.append(file)
    return res

def get_file_by_consult(id_user):
    """
    Récupère les fichiers consultés par un utilisateur.

    Args:
        id_user (int): L'ID de l'utilisateur.

    Returns:
        list: Une liste de fichiers consultés par l'utilisateur.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_files = session.query(ACONSULTE).filter_by(idPompier=id_user).order_by(asc(ACONSULTE.dateConsultation)).all()
    files = []
    for file in all_files:
        files.append(session.query(FICHIER).filter_by(idFichier=file.idFichier).first())
    session.close()
    return files

def get_file_by_extension(extension):
    """
    Récupère les fichiers de la base de données ayant une extension spécifique.

    Paramètres:
        extension (str): L'extension des fichiers à récupérer.
    
    Returns:
        list: Une liste de fichiers ayant l'extension donnée.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    files = session.query(FICHIER).filter_by(extensionFichier=extension).all()
    session.close()
    return files

def get_all_extension():
    """
    Récupère toutes les extensions de fichier uniques depuis la base de données.

    Returns:
        list: Une liste d'extensions de fichier uniques.
    """
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
    """
    Ajoute une catégorie à la base de données.

    Args:
        name (str): Le nom de la catégorie.
        parent_id (int): L'ID de la catégorie parente. Si None, la catégorie est une catégorie de premier niveau.

    Returns:
        None
    """
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
    """
    Met à jour le nom d'une catégorie dans la base de données.

    Args:
        category_id (int): L'ID de la catégorie à mettre à jour.
        name (str): Le nouveau nom de la catégorie.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    category = session.query(CATEGORIE).filter_by(idCategorie=category_id).first()
    category.nomCategorie = name
    session.commit()
    session.close()

def get_all_est_categorie():
    Session = sessionmaker(bind=db.engine)
    session = Session()
    all_est_categorie = session.query(table_EST_CATEGORIE).all()
    session.close()
    return all_est_categorie

def remove_category_from_database(category_id):
    """
    Supprime une catégorie et declasse ses fichiers associés.

    Args:
        category_id (int): L'ID de la catégorie à supprimer.

    Returns:
        None
    """
    sous_categories = get_liste_sous_categorie(category_id)
    Session = sessionmaker(bind=db.engine)
    session = Session()
    for sous_categorie in sous_categories:
        remove_category_from_database(sous_categorie.idCategorie)
    files = session.query(table_EST_CATEGORIE).filter_by(idCategorie=category_id).all()
    for file in files:
        other_categories = session.query(table_EST_CATEGORIE).filter(table_EST_CATEGORIE.c.idFichier == file.idFichier, table_EST_CATEGORIE.c.idCategorie != category_id).all()
        temp = other_categories
        for category in other_categories:
            if category in get_all_est_categorie():
                temp.remove(category)
        other_categories = temp
        if len(other_categories) == 0:
            session.query(table_EST_CATEGORIE).filter(table_EST_CATEGORIE.c.idFichier == file.idFichier, table_EST_CATEGORIE.c.idCategorie == 1).delete()
            session.query(table_EST_CATEGORIE).filter(table_EST_CATEGORIE.c.idFichier == file.idFichier, table_EST_CATEGORIE.c.idCategorie == category_id).update({table_EST_CATEGORIE.c.idCategorie: 1}, synchronize_session=False)
    session.query(table_SOUS_CATEGORIE).filter_by(categorieParent=category_id).delete()
    session.query(table_SOUS_CATEGORIE).filter_by(categorieEnfant=category_id).delete()
    session.query(CATEGORIE).filter_by(idCategorie=category_id).delete()
    session.commit()
    files = session.query(table_EST_CATEGORIE).filter_by(idCategorie=1).all()
    for file in files:
        file_category = session.query(table_EST_CATEGORIE).filter_by(idFichier=file.idFichier).all()
        if len(file_category) > 1:
            session.query(table_EST_CATEGORIE).filter_by(idFichier=file.idFichier, idCategorie=1).delete()
    session.commit()
    session.close()

def get_all_roles():
    """
    Récupère tous les rôles depuis la base de données.

    Returns:
        list: Une liste de rôles.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    extensions = session.query(ROLEPOMPIER.idRole,ROLEPOMPIER.nomRole).distinct().all()
    extensions_set = set()
    while extensions:
        extension = extensions.pop(0)
        extensions_set.add(str(extension[0])+" "+extension[1])
    session.close()
    return list(extensions_set)

def already_exist_mail(mail):
    """
    Vérifie si un utilisateur avec l'adresse e-mail donnée existe déjà dans la base de données.

    Args:
        mail (str): L'adresse e-mail à vérifier.

    Returns:
        bool: True si l'email existe déjà, False sinon.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    user = session.query(POMPIER).filter_by(emailPompier=mail).first()
    session.close()
    return user is not None

def get_user_access(id_user):
    """
    Récupère la liste des catégories d'accès pour un utilisateur donné.

    Paramètres:
        id_user (int): L'ID de l'utilisateur.

    Retourne:
        list: Une liste d'IDs de catégories d'accès.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    id_role = session.query(POMPIER.idRole).filter_by(idPompier=id_user).first()[0]
    list_access = []
    for row in session.query(table_A_ACCES.c.idCategorie).filter_by(idRole=id_role).all() :
        list_access.append(row[0])
    session.close()
    return list_access

def check_duplicate_user(first_name, last_name):
    """Vérifie si il y a deux utilisateurs avec le même nom et prénom

    Args:
        first_name (String): le prénom
        last_name (String): le nom

    Returns:
        Bool : True si il y a deux utilisateurs avec le même nom et prénom, False sinon
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    count = session.query(POMPIER).filter_by(nomPompier=last_name, prenomPompier=first_name).count()
    session.close()
    return count >= 2

def get_user_by_role(role):
    """Récupère tous les utilisateurs ayant un certain rôle

    Args:
        role (int): l'ID du rôle

    Returns:
        list: une liste d'utilisateurs
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    users = session.query(POMPIER).filter_by(idRole=role).all()
    session.close()
    return users

def update_user_role(id_user, role):
    """Met à jour le rôle d'un utilisateur

    Args:
        id_user (int): l'ID de l'utilisateur
        role (int): l'ID du nouveau rôle
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    user = get_user_by_id(id_user)
    user.idRole = role
    session.query(POMPIER).filter_by(idPompier=id_user).update({POMPIER.idRole: role}, synchronize_session=False)
    session.commit()
    session.close()

def get_category_by_role(role):
    """Récupère toutes les catégories accessibles par un certain rôle

    Args:
        role (int): l'ID du rôle

    Returns:
        list: une liste de catégories
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    categories = session.query(table_A_ACCES.c.idCategorie).filter_by(idRole=role).all()
    categories = [category[0] for category in categories]
    session.close()
    return categories

def modify_role_categories_database(role, categories):
    """Modifie les catégories accessibles par un certain rôle

    Args:
        role (int): l'ID du rôle
        categories (list): une liste d'IDs de catégories
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.query(table_A_ACCES).filter_by(idRole=role).delete()
    session.commit()
    for category in categories:
        session.execute(table_A_ACCES.insert().values(idRole=role, idCategorie=category))
    session.commit()
    session.close()
    
def add_role_to_databse(name, description, categories) :
    """Ajoute un rôle à la base de données

    Args:
        name (String): le nom du rôle
        description (String): la description du rôle
        categories (list): une liste d'IDs de catégories
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    role = ROLEPOMPIER(nomRole=name, descriptionRole=description)
    session.add(role)
    session.commit()
    for category in categories:
        session.execute(table_A_ACCES.insert().values(idRole=role.idRole, idCategorie=int(category)))
    session.commit()
    session.close()
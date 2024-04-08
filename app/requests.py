from app import db
from sqlalchemy.orm import sessionmaker
from app.models import (DATA, DOSSIER, RECHERCHE, ROLE, TAG,
                        t_A_ACCES, FICHIER, t_SOUS_DOSSIER,
                        UTILISATEUR, ARECHERCHE, ATAG, 
                        t_FAVORIS, NOTIFICATION, ARECHERCHE)
from unidecode import unidecode
import datetime
import random
import string

def get_user_by_id(id):
    return UTILISATEUR.query.filter_by(id_Utilisateur=id).first()

def get_root_dossiers():
    """ permet de récupérer les dossiers racines

    Returns:
        List : liste des dossiers racines
    """    
    all_dossiers = DOSSIER.query.all()
    root_dossiers = []
    for dossier in all_dossiers:
        if dossier.DOSSIER is None:
            root_dossiers.append(dossier)
    return root_dossiers

def update_dossier(id_dossier, nom = None, couleur = None, priorite = None):
    """ permet de mettre à jour un dossier

    Args:
        nom (str, optional): nom du dossier. Defaults to None.
        couleur (str, optional): couleur du dossier. Defaults to None.
        priorite (int, optional): priorité du dossier. Defaults to None.
        id_dossier (int, optional): id du dossier. Defaults to None.
    """    
    dossier = DOSSIER.query.filter_by(id_Dossier=id_dossier).first()
    if nom is not None:
        dossier.nom_Dossier = nom
    if couleur is not None:
        dossier.couleur_Dossier = couleur
    if priorite is not None:
        dossier.priorite_Dossier = priorite
    db.session.commit()

def update_dossier_priorite(id_dossier, priorite):
    """ permet de mettre à jour la priorité d'un dossier

    Args:
        id_dossier (int): id du dossier
        priorite (int): priorité du dossier
    """    
    dossier = DOSSIER.query.filter_by(id_Dossier=id_dossier).first()
    dossier.priorite_Dossier = priorite
    db.session.commit()

def add_file(file, filename, extension, tags, id_dossier):
    data = DATA(data=file)
    db.session.add(data)
    db.session.commit()
    file = FICHIER(nom_Fichier=filename, extension_Fichier=extension, id_Dossier=id_dossier, id_Data=data.id_Data)
    db.session.add(file)
    db.session.commit()
    for tag in tags:
        if not TAG.query.filter_by(nom_Tag=unidecode(tag[0].lower())).first():
            new_tag = TAG(nom_Tag=unidecode(tag[0].lower()))
            db.session.add(new_tag)
            db.session.commit()
        a_tag = ATAG(id_Fichier=file.id_Fichier, nom_Tag=unidecode(tag[0].lower()), nb_Occurrence=tag[1])
        db.session.add(a_tag)
        db.session.commit()
    return file.id_Fichier

def get_root_dossiers_by_role(id_role):
    """ permet de récupérer les dossiers racines en fonction du rôle

    Args:
        id_role (int): id du rôle

    Returns:
        List : liste des dossiers racines
    """    
    all_dossiers = DOSSIER.query.all()
    root_dossiers = []
    for dossier in all_dossiers:
        if dossier.DOSSIER is None and db.session.query(t_A_ACCES).filter(t_A_ACCES.c.id_Dossier == dossier.id_Dossier, t_A_ACCES.c.id_Role == id_role).first():
            root_dossiers.append(dossier)
    return root_dossiers

def get_files_favoris(user_id) :
    """
    Récupère les fichiers favoris d'un utilisateur.

    Args:
        user_id (int): L'identifiant de l'utilisateur.

    Returns:
        list: La liste des fichiers favoris de l'utilisateur.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    files = session.query(FICHIER).join(t_FAVORIS).filter(t_FAVORIS.c.id_Utilisateur == user_id).all()
    session.close()
    return files

def unfavorite_file(file_id, user_id):
    """
    Supprime un fichier des favoris d'un utilisateur.

    Args:
        user_id (int): L'identifiant de l'utilisateur.
        file_id (int): L'identifiant du fichier.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    session.query(t_FAVORIS).filter(t_FAVORIS.c.id_Utilisateur == user_id, t_FAVORIS.c.id_Fichier == file_id).delete()
    session.commit()
    session.close()

def favorite_file(file_id, user_id):
    """
    Ajoute un fichier aux favoris d'un utilisateur.

    Args:
        user_id (int): L'identifiant de l'utilisateur.
        file_id (int): L'identifiant du fichier.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    new_favorite = t_FAVORIS.insert().values(id_Utilisateur=user_id, id_Fichier=file_id)
    session.execute(new_favorite)
    session.commit()
    session.close()

def get_data_from_file_id(file_id: int):
    """
    Récupère les données d'un fichier en fonction de son identifiant.

    Args:
        file_id (int): L'identifiant du fichier.

    Returns:
        dict: Un dictionnaire contenant les informations du fichier.
    """
    db.session.query(DATA).join(FICHIER).filter(FICHIER.id_Fichier == file_id).first()

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
    user = session.query(UTILISATEUR).filter_by(email_Utilisateur=mail).first()
    session.close()
    return user is not None

def get_user_by_email(email):
    """
    Récupère un utilisateur en fonction de son adresse e-mail.

    Args:
        email (str): L'adresse e-mail de l'utilisateur.

    Returns:
        dict: Un dictionnaire contenant les informations de l'utilisateur.
    """
    return UTILISATEUR.query.filter_by(email_Utilisateur=email).first()

def add_user( prenom, nom, email, telephone,role, mdp,est_Actif_Utilisateur):
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
    id = UTILISATEUR.query.count() + 1
    user = UTILISATEUR(id_Utilisateur=id, nom_Utilisateur = nom,prenom_Utilisateur = prenom, email_Utilisateur = email, telephone_Utilisateur = telephone,
                   mdp_Utilisateur = mdp,est_Actif_Utilisateur=est_Actif_Utilisateur,id_Role = role)
    session.add(user)
    session.commit()
    session.close()

def generate_password() :
    """Génère un mot de passe aléatoire

    Returns:
        String: le mot de passe
    """    
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))

def create_notification(id_Utilisateur, id_Fichier, date_Heure_Notification,typeNotification):
    """
    Crée une notification pour un utilisateur.

    Args:
        id_Utilisateur (int): L'identifiant de l'utilisateur.
        id_Fichier (int): L'identifiant du fichier.
        date_Heure_Notification (str): La date et l'heure de la notification.
        typeNotification (str): Le type de la notification.

    Returns:
        None
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    id = NOTIFICATION.query.count() + 1
    notification = NOTIFICATION(id_Notification=id,id_Utilisateur=id_Utilisateur, id_Fichier=id_Fichier, date_Heure_Notification=date_Heure_Notification, typeNotification=typeNotification)
    session.add(notification)
    session.commit()
    session.close()

def recherche_exist(champ_Recherche):
    """ permet de savoir si une recherche existe

    Args:
        champ_Recherche (str): champ de recherche

    Returns:
        bool : True si la recherche existe, False sinon
    """    
    return RECHERCHE.query.filter_by(champ_Recherche=champ_Recherche).first() is not None


def create_recherche(champ_Recherche, id_Utilisateur):
    """ permet de créer une recherche

    Args:
        champ_Recherche (str): champ de recherche
        id_Utilisateur (int): id de l'utilisateur
    """    
    Session = sessionmaker(bind=db.engine)
    session = Session()
    if(recherche_exist(champ_Recherche) == False):
        recherche = RECHERCHE(champ_Recherche=champ_Recherche)
        session.add(recherche)
    arecherche=ARECHERCHE(id_Utilisateur=id_Utilisateur,champ_Recherche=champ_Recherche, date_Heure_Recherche=datetime.datetime.now())
    session.add(arecherche)
    session.commit()
    session.close()

def get_all_users():
    """ permet de récupérer tous les utilisateurs
    
    Returns:
    List : liste des utilisateurs
    """        
    return UTILISATEUR.query.all()

def get_recherche_by_user(id_utilisateur):
    """ permet de récupérer les recherches d'un utilisateur

    Args:
        id_utilisateur (int): id de l'utilisateur

    Returns:
        List : liste des recherches
    """    
    return ARECHERCHE.query.filter_by(id_Utilisateur=id_utilisateur).order_by(ARECHERCHE.date_Heure_Recherche.desc()).limit(10).all()

def delete_utilisateur(id_utilisateur):
    """ permet de supprimer un utilisateur et toutes les informations liées

    Args:
        id_utilisateur (int): id de l'utilisateur
    """    
    ARECHERCHE.query.filter_by(id_Utilisateur=id_utilisateur).delete()
    NOTIFICATION.query.filter_by(id_Utilisateur=id_utilisateur).delete()
    utilisateur = UTILISATEUR.query.filter_by(id_Utilisateur=id_utilisateur).first()
    db.session.delete(utilisateur)
    db.session.commit()

def update_role(id_utilisateur):
    """ permet de désactiver et d'activer un utilisateur

    Args:
        id_utilisateur (int): id de l'utilisateur
    """    
    utilisateur = UTILISATEUR.query.filter_by(id_Utilisateur=id_utilisateur).first()
    if utilisateur.est_Actif_Utilisateur == 1:
        utilisateur.est_Actif_Utilisateur = 0
    else:
        utilisateur.est_Actif_Utilisateur = 1
    db.session.commit()

def get_notifications_inscription_user():
    notifications = (
        db.session.query(NOTIFICATION, UTILISATEUR)
        .join(UTILISATEUR, NOTIFICATION.id_Utilisateur == UTILISATEUR.id_Utilisateur)
        .all()
    )
    return notifications

def get_role():
    """ permet de récupérer les rôles

    Returns:
        List : liste des rôles
    """    
    return ROLE.query.all()

def passif_to_actif(id_utilisateur):
    """ permet de passer un utilisateur de passif à actif

    Args:
        id_utilisateur (int): id de l'utilisateur
    """    
    utilisateur = UTILISATEUR.query.filter_by(id_Utilisateur=id_utilisateur).first()
    utilisateur.est_Actif_Utilisateur = 1
    db.session.commit()
def delete_notification(id_notification):
    """ permet de supprimer une notification

    Args:
        id_notification (int): id de la notification
    """    
    notification = NOTIFICATION.query.filter_by(id_Notification=id_notification).first()
    db.session.delete(notification)
    db.session.commit()

def change_role(id_utilisateur, nom_role):
    """ permet de changer le rôle d'un utilisateur

    Args:
        id_utilisateur (int): id de l'utilisateur
        id_role (int): id du rôle
    """    
    utilisateur = UTILISATEUR.query.filter_by(id_Utilisateur=id_utilisateur).first()
    role = ROLE.query.filter_by(nom_Role=nom_role).first()
    utilisateur.id_Role = role.id_Role
    db.session.commit()

def ok_inscrit(id_utilisateur,nom_role,id_Notification, password):
    """ permet de passer un utilisateur de inscrit à actif

    Args:
        id_utilisateur (int): id de l'utilisateur
    """    
    passif_to_actif(id_utilisateur)
    delete_notification(id_Notification)
    change_role(id_utilisateur,nom_role)
    change_password(id_utilisateur,password)

def get_data_by_file_id(file_id):
    return DATA.query.join(FICHIER).filter(FICHIER.id_Fichier == file_id).first()

def is_favorite_file(file_id, user_id):
    """
    Vérifie si un fichier est dans les favoris d'un utilisateur.

    Args:
        user_id (int): L'identifiant de l'utilisateur.
        file_id (int): L'identifiant du fichier.

    Returns:
        bool: True si le fichier est dans les favoris de l'utilisateur, False sinon.
    """
    Session = sessionmaker(bind=db.engine)
    session = Session()
    favorite = session.query(t_FAVORIS).filter(t_FAVORIS.c.id_Utilisateur == user_id, t_FAVORIS.c.id_Fichier == file_id).first()
    session.close()
    return favorite is not None

def change_password(id_utilisateur,mdp):
    """ permet de changer le mot de passe d'un utilisateur

    Args:
        id_utilisateur (int): id de l'utilisateur
        mdp (str): mot de passe
    """    
    utilisateur = UTILISATEUR.query.filter_by(id_Utilisateur=id_utilisateur).first()
    utilisateur.mdp_Utilisateur = mdp
    db.session.commit()

def refus_inscrit(id_utilisateur,id_Notification):
    """ permet de refuser l'inscription d'un utilisateur

    Args:
        id_utilisateur (int): id de l'utilisateur
    """    
    delete_utilisateur(id_utilisateur)
    delete_notification(id_Notification)
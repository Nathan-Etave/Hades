from app import db
from app.models import (DATA, DOSSIER, RECHERCHE, ROLE, TAG,
                        t_A_ACCES, FICHIER, t_SOUS_DOSSIER,
                        UTILISATEUR, ARECHERCHE, ATAG, 
                        t_FAVORIS, NOTIFICATION, ARECHERCHE)
from unidecode import unidecode

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
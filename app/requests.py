from app import db
from app.models import (DATA, DOSSIER, RECHERCHE, ROLE, TAG,
                        t_A_ACCES, FICHIER, t_SOUS_DOSSIER,
                        UTILISATEUR, t_A_RECHERCHE, ATAG, 
                        t_FAVORIS, NOTIFICATION)

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
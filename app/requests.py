from app import db
from app.models import (DATA, DOSSIER, RECHERCHE, ROLE, TAG,
                        t_A_ACCES, FICHIER, t_SOUS_DOSSIER,
                        UTILISATEUR, t_A_RECHERCHE, ATAG, 
                        t_FAVORIS, NOTIFICATION)

def get_user_by_id(id):
    return UTILISATEUR.query.filter_by(id_Utilisateur=id).first()

def get_root_dossiers():
    """ fonction qui retourne les dossiers racines

    Returns:
        List : liste des dossiers racines
    """    
    all_dossiers = DOSSIER.query.all()
    root_dossiers = []
    for dossier in all_dossiers:
        if dossier.DOSSIER is None:
            root_dossiers.append(dossier)
    return root_dossiers

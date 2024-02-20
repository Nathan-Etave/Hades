from app import db
from sqlalchemy.orm import sessionmaker
from app.models import (DATA, DOSSIER, RECHERCHE, ROLE, TAG,
                        t_A_ACCES, FICHIER, t_SOUS_DOSSIER,
                        UTILISATEUR, t_A_RECHERCHE, ATAG, 
                        t_FAVORIS, NOTIFICATION)

def get_user_by_id(id):
    return UTILISATEUR.query.filter_by(id_Utilisateur=id).first()

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

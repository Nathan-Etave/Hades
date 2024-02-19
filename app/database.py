from app import app, db
from app.models import (DATA, DOSSIER, RECHERCHE, ROLE, TAG,
                        t_A_ACCES, FICHIER, t_SOUS_DOSSIER,
                        UTILISATEUR, t_A_RECHERCHE, ATAG, 
                        t_FAVORIS, NOTIFICATION)
from sqlalchemy.orm import sessionmaker
import csv
import sys

maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

@app.cli.command('init_database')
def init_database():
    """Initialise la base de données avec les données des fichiers CSV
    """    
    
    db.create_all()
    Session = sessionmaker(bind=db.engine)
    session = Session()

    with open('app/static/csv/DATA.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            data = DATA(id_Data=row[0], data=row[1])
            session.add(data)
    session.commit()

    with open('app/static/csv/DOSSIER.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            dossier = DOSSIER(id_Dossier=row[0], nom_Dossier=row[1], priorite_Dossier=row[2], couleur=row[3])
            session.add(dossier)
    session.commit()

    with open('app/static/csv/RECHERCHE.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            recherche = RECHERCHE(champ_Recherche=row[0], date_Heure_Recherche=row[1])
            session.add(recherche)
    session.commit()

    with open('app/static/csv/ROLE.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            role = ROLE(id_Role=row[0], nom_Role=row[1])
            session.add(role)
    session.commit()

    with open('app/static/csv/TAG.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            tag = TAG(nom_Tag=row[0])
            session.add(tag)
    session.commit()

    with open('app/static/csv/A_ACCES.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            a_acces = t_A_ACCES.insert().values(id_Role=row[0], id_Dossier=row[1])
            session.execute(a_acces)
    session.commit()

    with open('app/static/csv/FICHIER.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            fichier = FICHIER(id_Fichier=row[0], nom_Fichier=row[1], date_Heure_Fichier=row[2], id_Dossier=row[3], id_Data=row[4])
            session.add(fichier)
    session.commit()

    with open('app/static/csv/SOUS_DOSSIER.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            sous_dossier = t_SOUS_DOSSIER(id_Dossier_Parent=row[0], id_Dossier_Enfant=row[1])
            session.add(sous_dossier)
    session.commit()

    with open('app/static/csv/UTILISATEUR.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            utilisateur = UTILISATEUR(id_Utilisateur=row[0], nom_Utilisateur=row[1], prenom_Utilisateur=row[2], email_Utilisateur=row[3], mdp_Utilisateur=row[4], telephone_Utilisateur=row[5], est_Actif_Utilisateur=row[6], id_Role=row[7])
            session.add(utilisateur)
    session.commit()

    with open('app/static/csv/A_RECHERCHE.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            a_recherche = t_A_RECHERCHE.insert().values(id_Utilisateur=row[0], champ_Recherche=row[1])
            session.execute(a_recherche)
    session.commit()

    with open('app/static/csv/ATAG.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            atag = ATAG(id_Fichier=row[0], nom_Tag=row[1])
            session.add(atag)
    session.commit()

    with open('app/static/csv/FAVORIS.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            favoris = t_FAVORIS.insert().values(id_Utilisateur=row[0], id_Fichier=row[1])
            session.execute(favoris)
    session.commit()

    with open('app/static/csv/NOTIFICATION.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            notification = NOTIFICATION(id_Notification=row[0], id_Utilisateur=row[1], message_Notification=row[2], date_Heure_Notification=row[3])
            session.add(notification)
    session.commit()
    session.close()
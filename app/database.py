from app import app, db
from app.models import (TAG, ETATFICHIER, FICHIER, NOTIFICATION, CATEGORIE, ROLEPOMPIER, POMPIER, SIGNALEMENT,
                        DATE, ACONSULTE, ANOTIFICATION, table_FAVORI, table_SOUS_CATEGORIE, table_EST_CATEGORIE,
                        table_HISTORIQUE, table_A_TAG, table_A_ACCES)
from sqlalchemy.orm import sessionmaker
from datetime import datetime
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
    
    db.create_all()
    Session = sessionmaker(bind=db.engine)
    session = Session()

    with open('app/static/csv/TAG.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            tag = TAG(nomTag=row[0])
            db.session.add(tag)
    db.session.commit()

    with open('app/static/csv/ETAT_FICHIER.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            etat = ETATFICHIER(nomEtatFichier=row[1], descriptionEtatFichier=row[2])
            db.session.add(etat)
    db.session.commit()

    with open('app/static/csv/FICHIER.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            fichier = FICHIER(nomFichier=row[1], data=bytes(row[2], 'utf-8'), extensionFichier=row[3], idEtatFichier=row[4])
            db.session.add(fichier)
    db.session.commit()

    with open('app/static/csv/NOTIFICATION.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            notif = NOTIFICATION(texteNotification=row[1], typeChange=row[2], raisonNotification=row[3])
            db.session.add(notif)
    db.session.commit()

    with open('app/static/csv/CATEGORIE.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            categorie = CATEGORIE(nomCategorie=row[1])
            db.session.add(categorie)
    db.session.commit()

    with open('app/static/csv/ROLE_POMPIER.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            role = ROLEPOMPIER(nomRole=row[1], descriptionRole=row[2])
            db.session.add(role)
    db.session.commit()

    with open('app/static/csv/POMPIER.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            pompier = POMPIER(nomPompier=row[1], prenomPompier=row[2], emailPompier=row[3], telephonePompier=row[4], mdpPompier=row[5], photoPompier=bytes(row[6], 'utf-8'), idRole=row[7])
            db.session.add(pompier)
    db.session.commit()

    with open('app/static/csv/SIGNALEMENT.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            signalement = SIGNALEMENT(idFichier=row[0], idPompier=row[1], idDate=row[2], descriptionSignalement=row[3])
            db.session.add(signalement)
    db.session.commit()

    with open('app/static/csv/FAVORI.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            session.execute(table_FAVORI.insert().values(idFichier=row[0], idPompier=row[1]))
            session.commit()

    with open('app/static/csv/DATE.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            date = DATE(laDate=datetime.fromisoformat(row[1]))
            db.session.add(date)
    db.session.commit()

    with open('app/static/csv/A_CONSULTE.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            a_consulte = ACONSULTE(idFichier=row[0], idPompier=row[1], idDate=row[2])
            db.session.add(a_consulte)
    db.session.commit()

    with open('app/static/csv/SOUS_CATEGORIE.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            session.execute(table_SOUS_CATEGORIE.insert().values(categorieParent=row[0], categorieEnfant=row[1]))
            session.commit()

    with open('app/static/csv/EST_CATEGORIE.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            session.execute(table_EST_CATEGORIE.insert().values(idCategorie=row[0], idFichier=row[1]))
            session.commit()

    with open('app/static/csv/HISTORIQUE.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            session.execute(table_HISTORIQUE.insert().values(nouvelleVersion=row[0], ancienneVersion=row[1]))
            session.commit()

    with open('app/static/csv/A_TAG.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            session.execute(table_A_TAG.insert().values(nomTag=row[0], idFichier=row[1]))
            session.commit()

    with open('app/static/csv/A_NOTIFICATION.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            a_notif = ANOTIFICATION(idNotification=row[0], idPompier=row[1], idFichier=row[2], idDate=row[3])
            db.session.add(a_notif)
    db.session.commit()

    with open('app/static/csv/A_ACCES.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            session.execute(table_A_ACCES.insert().values(idCategorie=row[0], idRole=row[1]))
            session.commit()
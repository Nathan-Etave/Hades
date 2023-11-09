from app import db
from typing import List, Optional
from sqlalchemy import Column, Date, ForeignKeyConstraint, Index, String, Table
from sqlalchemy.dialects.mysql import INTEGER, BLOB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = db.Model
metadata = Base.metadata

class CATEGORIE(Base):
    __tablename__ = 'CATEGORIE'

    id = mapped_column(INTEGER(11), primary_key=True)
    nom = mapped_column(String(255))

    ROLE_POMPIER: Mapped['ROLEPOMPIER'] = relationship('ROLEPOMPIER', secondary='A_ACCES', back_populates='CATEGORIE_')
    CATEGORIE: Mapped['CATEGORIE'] = relationship('CATEGORIE', secondary='SOUS_CATEGORIE', primaryjoin=lambda: CATEGORIE.idCategorie == table_SOUS_CATEGORIE.c.categorieEnfant, secondaryjoin=lambda: CATEGORIE.idCategorie == table_SOUS_CATEGORIE.c.categorieParent, back_populates='CATEGORIE_')
    CATEGORIE_: Mapped['CATEGORIE'] = relationship('CATEGORIE', secondary='SOUS_CATEGORIE', primaryjoin=lambda: CATEGORIE.idCategorie == table_SOUS_CATEGORIE.c.categorieParent, secondaryjoin=lambda: CATEGORIE.idCategorie == table_SOUS_CATEGORIE.c.categorieEnfant, back_populates='CATEGORIE')
    FICHIER: Mapped['FICHIER'] = relationship('FICHIER', secondary='EST_CATEGORIE', back_populates='CATEGORIE_')


class DATE(Base):
    __tablename__ = 'DATE'

    idDate = mapped_column(INTEGER(11), primary_key=True)
    laDate = mapped_column(Date)

    A_CONSULTE: Mapped[List['ACONSULTE']] = relationship('ACONSULTE', uselist=True, back_populates='DATE_')
    A_NOTIFICATION: Mapped[List['ANOTIFICATION']] = relationship('ANOTIFICATION', uselist=True, back_populates='DATE_')


class ETATFICHIER(Base):
    __tablename__ = 'ETAT_FICHIER'

    idEtatFichier = mapped_column(INTEGER(11), primary_key=True)
    nomEtatFichier = mapped_column(String(255))
    descriptionEtatFichier = mapped_column(String(255))

    FICHIER: Mapped[List['FICHIER']] = relationship('FICHIER', uselist=True, back_populates='ETAT_FICHIER')


class NOTIFICATION(Base):
    __tablename__ = 'NOTIFICATION'

    idNotification = mapped_column(INTEGER(11), primary_key=True)
    precision = mapped_column(String(255))
    typechangement = mapped_column(String(255))
    raison = mapped_column(String(255))

    A_NOTIFICATION: Mapped[List['ANOTIFICATION']] = relationship('ANOTIFICATION', uselist=True, back_populates='NOTIFICATION_')


class ROLEPOMPIER(Base):
    __tablename__ = 'ROLE_POMPIER'

    idRole = mapped_column(INTEGER(11), primary_key=True)
    nomRole = mapped_column(String(255))
    descriptionRole = mapped_column(String(255))

    CATEGORIE_: Mapped['CATEGORIE'] = relationship('CATEGORIE', secondary='A_ACCES', back_populates='ROLE_POMPIER')
    POMPIER: Mapped[List['POMPIER']] = relationship('POMPIER', uselist=True, back_populates='ROLE_POMPIER')


class TAG(Base):
    __tablename__ = 'TAG'

    nomTag = mapped_column(String(255), primary_key=True)

    FICHIER: Mapped['FICHIER'] = relationship('FICHIER', secondary='A_TAG', back_populates='TAG_')


table_A_ACCES = Table(
    'A_ACCES', metadata,
    Column('idCategorie', INTEGER(11), primary_key=True, nullable=False),
    Column('idRole', INTEGER(11), primary_key=True, nullable=False),
    ForeignKeyConstraint(['idCategorie'], ['CATEGORIE.idCategorie'], name='FKacces_categorie'),
    ForeignKeyConstraint(['idRole'], ['ROLE_POMPIER.idRole'], name='FKacces_role'),
    Index('FKacces_role', 'idRole')
)


class FICHIER(Base):
    __tablename__ = 'FICHIER'
    __table_args__ = (
        ForeignKeyConstraint(['idEtatFichier'], ['ETAT_FICHIER.idEtatFichier'], name='FKfichier_etat'),
        Index('FKfichier_etat', 'idEtatFichier')
    )

    id = mapped_column(INTEGER(11), primary_key=True)
    nom = mapped_column(String(255))
    data = mapped_column(BLOB)
    extension = mapped_column(String(255))
    idEtatFichier = mapped_column(INTEGER(11))
    @property
    def taille(self):
        if len(self.leFichier) < 10**6:
            return str(round(len(self.leFichier)/10**3, 2)) + " ko"
        elif len(self.leFichier) < 10**9:
            return str(round(len(self.leFichier)/10**6, 2)) + " Mo"
        else:
            return str(round(len(self.leFichier)/10**9, 2)) + " Go"
    

    CATEGORIE_: Mapped['CATEGORIE'] = relationship('CATEGORIE', secondary='EST_CATEGORIE', back_populates='FICHIER')
    ETAT_FICHIER: Mapped[Optional['ETATFICHIER']] = relationship('ETATFICHIER', back_populates='FICHIER')
    TAG_: Mapped['TAG'] = relationship('TAG', secondary='A_TAG', back_populates='FICHIER')
    POMPIER: Mapped['POMPIER'] = relationship('POMPIER', secondary='FAVORI', back_populates='FICHIER_')
    FICHIER: Mapped['FICHIER'] = relationship('FICHIER', secondary='HISTORIQUE', primaryjoin=lambda: FICHIER.idFichier == table_HISTORIQUE.c.ancienneVersion, secondaryjoin=lambda: FICHIER.idFichier == table_HISTORIQUE.c.nouvelleVersion, back_populates='FICHIER_')
    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', secondary='HISTORIQUE', primaryjoin=lambda: FICHIER.idFichier == table_HISTORIQUE.c.nouvelleVersion, secondaryjoin=lambda: FICHIER.idFichier == table_HISTORIQUE.c.ancienneVersion, back_populates='FICHIER')
    A_CONSULTE: Mapped[List['ACONSULTE']] = relationship('ACONSULTE', uselist=True, back_populates='FICHIER_')
    A_NOTIFICATION: Mapped[List['ANOTIFICATION']] = relationship('ANOTIFICATION', uselist=True, back_populates='FICHIER_')
    SIGNALEMENT: Mapped[List['SIGNALEMENT']] = relationship('SIGNALEMENT', uselist=True, back_populates='FICHIER_')


class POMPIER(Base):
    __tablename__ = 'POMPIER'
    __table_args__ = (
        ForeignKeyConstraint(['idRole'], ['ROLE_POMPIER.idRole'], name='FKpompier_rolePompier'),
        Index('FKpompier_rolePompier', 'idRole')
    )

    id = mapped_column(INTEGER(11), primary_key=True)
    nom = mapped_column(String(255))
    prenom = mapped_column(String(255))
    mail = mapped_column(String(255))
    telephone = mapped_column(String(255))
    mdp = mapped_column(String(255))
    photo = mapped_column(BLOB)
    idRole = mapped_column(INTEGER(11))

    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', secondary='FAVORI', back_populates='POMPIER')
    ROLE_POMPIER: Mapped[Optional['ROLEPOMPIER']] = relationship('ROLEPOMPIER', back_populates='POMPIER')
    A_CONSULTE: Mapped[List['ACONSULTE']] = relationship('ACONSULTE', uselist=True, back_populates='POMPIER_')
    A_NOTIFICATION: Mapped[List['ANOTIFICATION']] = relationship('ANOTIFICATION', uselist=True, back_populates='POMPIER_')
    SIGNALEMENT: Mapped[List['SIGNALEMENT']] = relationship('SIGNALEMENT', uselist=True, back_populates='POMPIER_')


table_SOUS_CATEGORIE = Table(
    'SOUS_CATEGORIE', metadata,
    Column('categorieParent', INTEGER(11), primary_key=True, nullable=False),
    Column('categorieEnfant', INTEGER(11), primary_key=True, nullable=False),
    ForeignKeyConstraint(['categorieEnfant'], ['CATEGORIE.idCategorie'], name='FKcategorieEnfant_categorie'),
    ForeignKeyConstraint(['categorieParent'], ['CATEGORIE.idCategorie'], name='FKcategorieParent_categorie'),
    Index('FKcategorieParent_categorie', 'categorieParent')
)


class ACONSULTE(Base):
    __tablename__ = 'A_CONSULTE'
    __table_args__ = (
        ForeignKeyConstraint(['idDate'], ['DATE.idDate'], name='FKa_consulte_date'),
        ForeignKeyConstraint(['idFichier'], ['FICHIER.idFichier'], name='FKa_consulte_fichier'),
        ForeignKeyConstraint(['idPompier'], ['POMPIER.idPompier'], name='FKa_consulte_pompier'),
        Index('FKa_consulte_date', 'idDate'),
        Index('FKa_consulte_pompier', 'idPompier')
    )

    idFichier = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    idPompier = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    idDate = mapped_column(INTEGER(11), primary_key=True, nullable=False)

    DATE_: Mapped['DATE'] = relationship('DATE', back_populates='A_CONSULTE')
    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', back_populates='A_CONSULTE')
    POMPIER_: Mapped['POMPIER'] = relationship('POMPIER', back_populates='A_CONSULTE')


class ANOTIFICATION(Base):
    __tablename__ = 'A_NOTIFICATION'
    __table_args__ = (
        ForeignKeyConstraint(['idDate'], ['DATE.idDate'], name='FKnotif_date'),
        ForeignKeyConstraint(['idFichier'], ['FICHIER.idFichier'], name='FKnotif_fichier'),
        ForeignKeyConstraint(['idNotification'], ['NOTIFICATION.idNotification'], name='FKnotif_notif'),
        ForeignKeyConstraint(['idPompier'], ['POMPIER.idPompier'], name='FKnotif_pompier'),
        Index('FKnotif_date', 'idDate'),
        Index('FKnotif_fichier', 'idFichier'),
        Index('FKnotif_pompier', 'idPompier')
    )

    idNotification = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    idPompier = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    idFichier = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    idDate = mapped_column(INTEGER(11), primary_key=True, nullable=False)

    DATE_: Mapped['DATE'] = relationship('DATE', back_populates='A_NOTIFICATION')
    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', back_populates='A_NOTIFICATION')
    NOTIFICATION_: Mapped['NOTIFICATION'] = relationship('NOTIFICATION', back_populates='A_NOTIFICATION')
    POMPIER_: Mapped['POMPIER'] = relationship('POMPIER', back_populates='A_NOTIFICATION')


table_A_TAG = Table(
    'A_TAG', metadata,
    Column('nomTag', String(255), primary_key=True, nullable=False),
    Column('idFichier', INTEGER(11), primary_key=True, nullable=False),
    ForeignKeyConstraint(['idFichier'], ['FICHIER.idFichier'], name='FKtag_fic'),
    ForeignKeyConstraint(['nomTag'], ['TAG.nomTag'], name='FKTag'),
    Index('FKtag_fic', 'idFichier')
)


table_EST_CATEGORIE = Table(
    'EST_CATEGORIE', metadata,
    Column('idCategorie', INTEGER(11), primary_key=True, nullable=False),
    Column('idFichier', INTEGER(11), primary_key=True, nullable=False),
    ForeignKeyConstraint(['idCategorie'], ['CATEGORIE.idCategorie'], name='FKest_Categorie'),
    ForeignKeyConstraint(['idFichier'], ['FICHIER.idFichier'], name='FKest_cat_fichier'),
    Index('FKest_cat_fichier', 'idFichier')
)


table_FAVORI = Table(
    'FAVORI', metadata,
    Column('idFichier', INTEGER(11), primary_key=True, nullable=False),
    Column('idPompier', INTEGER(11), primary_key=True, nullable=False),
    ForeignKeyConstraint(['idFichier'], ['FICHIER.idFichier'], name='FKfavori_fichier'),
    ForeignKeyConstraint(['idPompier'], ['POMPIER.idPompier'], name='FKfavori_pompier'),
    Index('FKfavori_pompier', 'idPompier')
)


table_HISTORIQUE = Table(
    'HISTORIQUE', metadata,
    Column('nouvelleVersion', INTEGER(11), primary_key=True, nullable=False),
    Column('ancienneVersion', INTEGER(11), primary_key=True, nullable=False),
    ForeignKeyConstraint(['ancienneVersion'], ['FICHIER.idFichier'], name='FKancienneVersion_fichier'),
    ForeignKeyConstraint(['nouvelleVersion'], ['FICHIER.idFichier'], name='FKnouvelleVersion_fichier'),
    Index('FKancienneVersion_fichier', 'ancienneVersion')
)


class SIGNALEMENT(Base):
    __tablename__ = 'SIGNALEMENT'
    __table_args__ = (
        ForeignKeyConstraint(['idFichier'], ['FICHIER.idFichier'], name='FKsignalement_fichier'),
        ForeignKeyConstraint(['idPompier'], ['POMPIER.idPompier'], name='FKsignalement_pompier'),
        Index('FKsignalement_pompier', 'idPompier')
    )

    idFichier = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    idPompier = mapped_column(INTEGER(11), primary_key=True, nullable=False)
    descriptionSignalement = mapped_column(String(255))

    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', back_populates='SIGNALEMENT')
    POMPIER_: Mapped['POMPIER'] = relationship('POMPIER', back_populates='SIGNALEMENT')
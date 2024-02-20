from app import db
from flask_login import UserMixin
from typing import List, Optional
from sqlalchemy import Column, ForeignKeyConstraint, Index, String, Table, Integer, DateTime, BLOB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = db.Model
metadata = Base.metadata

class DATA(Base):
    __tablename__ = 'DATA'

    id_Data = mapped_column(Integer, primary_key=True)
    data = mapped_column(BLOB)

    FICHIER: Mapped[List['FICHIER']] = relationship('FICHIER', uselist=True, back_populates='DATA_')


class DOSSIER(Base):
    __tablename__ = 'DOSSIER'

    id_Dossier = mapped_column(Integer, primary_key=True)
    nom_Dossier = mapped_column(String(255))
    priorite_Dossier = mapped_column(Integer)
    couleur_Dossier = mapped_column(String(255))

    ROLE: Mapped['ROLE'] = relationship('ROLE', secondary='A_ACCES', back_populates='DOSSIER_')
    DOSSIER: Mapped['DOSSIER'] = relationship('DOSSIER', secondary='SOUS_DOSSIER', primaryjoin=lambda: DOSSIER.id_Dossier == t_SOUS_DOSSIER.c.id_Dossier_Enfant, secondaryjoin=lambda: DOSSIER.id_Dossier == t_SOUS_DOSSIER.c.id_Dossier_Parent, back_populates='DOSSIER_')
    DOSSIER_: Mapped['DOSSIER'] = relationship('DOSSIER', secondary='SOUS_DOSSIER', primaryjoin=lambda: DOSSIER.id_Dossier == t_SOUS_DOSSIER.c.id_Dossier_Parent, secondaryjoin=lambda: DOSSIER.id_Dossier == t_SOUS_DOSSIER.c.id_Dossier_Enfant, back_populates='DOSSIER')
    FICHIER: Mapped[List['FICHIER']] = relationship('FICHIER', uselist=True, back_populates='DOSSIER_')


class RECHERCHE(Base):
    __tablename__ = 'RECHERCHE'

    champ_Recherche = mapped_column(String(255), primary_key=True)
    date_Heure_Recherche = mapped_column(DateTime)

    UTILISATEUR: Mapped['UTILISATEUR'] = relationship('UTILISATEUR', secondary='A_RECHERCHE', back_populates='RECHERCHE_')


class ROLE(Base):
    __tablename__ = 'ROLE'

    id_Role = mapped_column(Integer, primary_key=True)
    nom_Role = mapped_column(String(255))

    DOSSIER_: Mapped['DOSSIER'] = relationship('DOSSIER', secondary='A_ACCES', back_populates='ROLE')
    UTILISATEUR: Mapped[List['UTILISATEUR']] = relationship('UTILISATEUR', uselist=True, back_populates='ROLE_')


class TAG(Base):
    __tablename__ = 'TAG'

    nom_Tag = mapped_column(String(255), primary_key=True)

    A_TAG: Mapped[List['ATAG']] = relationship('ATAG', uselist=True, back_populates='TAG_')


t_A_ACCES = Table(
    'A_ACCES', metadata,
    Column('id_Role', Integer, primary_key=True, nullable=False),
    Column('id_Dossier', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['id_Dossier'], ['DOSSIER.id_Dossier'], name='fk_A_Acces_Dossier'),
    ForeignKeyConstraint(['id_Role'], ['ROLE.id_Role'], name='fk_A_Acces_Role'),
    Index('fk_A_Acces_Dossier', 'id_Dossier')
)


class FICHIER(Base):
    __tablename__ = 'FICHIER'
    __table_args__ = (
        ForeignKeyConstraint(['id_Data'], ['DATA.id_Data'], name='fk_Fichier_Data'),
        ForeignKeyConstraint(['id_Dossier'], ['DOSSIER.id_Dossier'], name='fk_Fichier_Dossier'),
        Index('fk_Fichier_Data', 'id_Data'),
        Index('fk_Fichier_Dossier', 'id_Dossier')
    )

    id_Fichier = mapped_column(Integer, primary_key=True)
    nom_Fichier = mapped_column(String(255))
    extension_Fichier = mapped_column(String(255))
    id_Dossier = mapped_column(Integer)
    id_Data = mapped_column(Integer)
    @property
    def taille(self):
        if len(self.DATA_.data) < 10**6:
            return str(round(len(self.DATA_.data)/10**3, 2)) + "\u00A0ko"
        elif len(self.DATA_.data) < 10**9:
            return str(round(len(self.DATA_.data)/10**6, 2)) + "\u00A0Mo"
        else:
            return str(round(len(self.DATA_.data)/10**9, 2)) + "\u00A0Go"

    DATA_: Mapped[Optional['DATA']] = relationship('DATA', back_populates='FICHIER')
    DOSSIER_: Mapped[Optional['DOSSIER']] = relationship('DOSSIER', back_populates='FICHIER')
    UTILISATEUR: Mapped['UTILISATEUR'] = relationship('UTILISATEUR', secondary='FAVORIS', back_populates='FICHIER_')
    A_TAG: Mapped[List['ATAG']] = relationship('ATAG', uselist=True, back_populates='FICHIER_')
    NOTIFICATION: Mapped[List['NOTIFICATION']] = relationship('NOTIFICATION', uselist=True, back_populates='FICHIER_')


t_SOUS_DOSSIER = Table(
    'SOUS_DOSSIER', metadata,
    Column('id_Dossier_Parent', Integer, primary_key=True, nullable=False),
    Column('id_Dossier_Enfant', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['id_Dossier_Enfant'], ['DOSSIER.id_Dossier'], name='fk_Sous_Dossier_Enfant'),
    ForeignKeyConstraint(['id_Dossier_Parent'], ['DOSSIER.id_Dossier'], name='fk_Sous_Dossier_Parent'),
    Index('fk_Sous_Dossier_Enfant', 'id_Dossier_Enfant')
)


class UTILISATEUR(Base, UserMixin):
    __tablename__ = 'UTILISATEUR'
    __table_args__ = (
        ForeignKeyConstraint(['id_Role'], ['ROLE.id_Role'], name='fk_Utilisateur_Role'),
        Index('fk_Utilisateur_Role', 'id_Role')
    )

    id_Utilisateur = mapped_column(Integer, primary_key=True)
    nom_Utilisateur = mapped_column(String(255))
    prenom_Utilisateur = mapped_column(String(255))
    email_Utilisateur = mapped_column(String(255))
    mdp_Utilisateur = mapped_column(String(255))
    telephone_Utilisateur = mapped_column(Integer)
    est_Actif_Utilisateur = mapped_column(Integer)
    id_Role = mapped_column(Integer)

    def get_id(self):
        return self.id_Utilisateur

    RECHERCHE_: Mapped['RECHERCHE'] = relationship('RECHERCHE', secondary='A_RECHERCHE', back_populates='UTILISATEUR')
    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', secondary='FAVORIS', back_populates='UTILISATEUR')
    ROLE_: Mapped[Optional['ROLE']] = relationship('ROLE', back_populates='UTILISATEUR')
    NOTIFICATION: Mapped[List['NOTIFICATION']] = relationship('NOTIFICATION', uselist=True, back_populates='UTILISATEUR_')


t_A_RECHERCHE = Table(
    'A_RECHERCHE', metadata,
    Column('id_Utilisateur', Integer, primary_key=True, nullable=False),
    Column('champ_Recherche', String(255), primary_key=True, nullable=False),
    ForeignKeyConstraint(['champ_Recherche'], ['RECHERCHE.champ_Recherche'], name='fk_A_Recherche_Recherche'),
    ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_A_Recherche_Utilisateur'),
    Index('fk_A_Recherche_Recherche', 'champ_Recherche')
)


class ATAG(Base):
    __tablename__ = 'A_TAG'
    __table_args__ = (
        ForeignKeyConstraint(['id_Fichier'], ['FICHIER.id_Fichier'], name='fk_A_Tag_Fichier'),
        ForeignKeyConstraint(['nom_Tag'], ['TAG.nom_Tag'], name='fk_A_Tag_Tag'),
        Index('fk_A_Tag_Tag', 'nom_Tag')
    )

    id_Fichier = mapped_column(Integer, primary_key=True, nullable=False)
    nom_Tag = mapped_column(String(255), primary_key=True, nullable=False)
    nb_Occurrence = mapped_column(Integer)

    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', back_populates='A_TAG')
    TAG_: Mapped['TAG'] = relationship('TAG', back_populates='A_TAG')


t_FAVORIS = Table(
    'FAVORIS', metadata,
    Column('id_Utilisateur', Integer, primary_key=True, nullable=False),
    Column('id_Fichier', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['id_Fichier'], ['FICHIER.id_Fichier'], name='fk_Favoris_Fichier'),
    ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_Favoris_Utilisateur'),
    Index('fk_Favoris_Fichier', 'id_Fichier')
)


class NOTIFICATION(Base):
    __tablename__ = 'NOTIFICATION'
    __table_args__ = (
        ForeignKeyConstraint(['id_Fichier'], ['FICHIER.id_Fichier'], name='fk_Notification_Fichier'),
        ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_Notification_Utilisateur'),
        Index('fk_Notification_Fichier', 'id_Fichier'),
        Index('fk_Notification_Utilisateur', 'id_Utilisateur')
    )

    id_Notification = mapped_column(Integer, primary_key=True)
    date_Heure_Notification = mapped_column(DateTime)
    typeNotification = mapped_column(String(255))
    id_Utilisateur = mapped_column(Integer)
    id_Fichier = mapped_column(Integer)

    FICHIER_: Mapped[Optional['FICHIER']] = relationship('FICHIER', back_populates='NOTIFICATION')
    UTILISATEUR_: Mapped[Optional['UTILISATEUR']] = relationship('UTILISATEUR', back_populates='NOTIFICATION')

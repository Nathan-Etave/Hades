from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, ForeignKeyConstraint, Index, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.extensions import db

class FICHIER(db.Model):
    __tablename__ = 'FICHIER'
    __table_args__ = (
        ForeignKeyConstraint(['id_Dossier'], ['DOSSIER.id_Dossier'], name='fk_Fichier_Dossier'),
        ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_Fichier_Utilisateur'),
        Index('fk_Fichier_Dossier', 'id_Dossier'),
        Index('fk_Fichier_Utilisateur', 'id_Utilisateur')
    )

    id_Fichier = mapped_column(Integer, primary_key=True)
    id_Dossier = mapped_column(Integer)
    nom_Fichier = mapped_column(String(255))
    extension_Fichier = mapped_column(String(255))
    date_Fichier = mapped_column(DateTime, default=datetime.now())
    id_Utilisateur = mapped_column(Integer)
    
    def to_dict(self):
       result = {}
       for c in self.__table__.columns:
           if c.name == 'date_Fichier':
               result[c.name] = self.date_Fichier.strftime('%d/%m/%Y %H:%M:%S:%f')
           else:
               result[c.name] = getattr(self, c.name)
       return result

    DOSSIER_: Mapped[Optional['DOSSIER']] = relationship('DOSSIER', back_populates='FICHIER')
    UTILISATEUR_: Mapped[List['UTILISATEUR']] = relationship('UTILISATEUR', secondary='FAVORIS', back_populates='FICHIER_')
    AUTEUR: Mapped[Optional['UTILISATEUR']] = relationship('UTILISATEUR', back_populates='FICHIER_')
    A_TAG: Mapped[List['A_TAG']] = relationship('A_TAG', uselist=True, back_populates='FICHIER_')
    NOTIFICATION: Mapped[List['NOTIFICATION']] = relationship('NOTIFICATION', uselist=True, back_populates='FICHIER_')
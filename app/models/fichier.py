from typing import List, Optional
from sqlalchemy import Integer, String, ForeignKeyConstraint, Index
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.extensions import db
from app.models.a_tag import A_TAG

class FICHIER(db.Model):
    __tablename__ = 'FICHIER'
    __table_args__ = (
        ForeignKeyConstraint(['id_Dossier'], ['DOSSIER.id_Dossier'], name='fk_Fichier_Dossier'),
        Index('fk_Fichier_Dossier', 'id_Dossier')
    )

    id_Fichier = mapped_column(Integer, primary_key=True)
    id_Dossier = mapped_column(Integer)
    URI_Fichier = mapped_column(String(255))

    A_TAG: Mapped[List['A_TAG']] = relationship('A_TAG', uselist=True, back_populates='FICHIER_')

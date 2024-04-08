from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.extensions import db
from app.models.dossier import DOSSIER
from app.models.a_acces import A_ACCES

class ROLE(db.Model):
    __tablename__ = 'ROLE'

    id_Role = mapped_column(Integer, primary_key=True)
    nom_Role = mapped_column(String(255))

    DOSSIER_: Mapped['DOSSIER'] = relationship('DOSSIER', secondary='A_ACCES', back_populates='ROLE')

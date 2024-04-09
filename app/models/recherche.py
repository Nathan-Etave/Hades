from typing import List
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.extensions import db


class RECHERCHE(db.Model):
    __tablename__ = 'RECHERCHE'

    champ_Recherche = mapped_column(String(255), primary_key=True)

    A_RECHERCHE: Mapped[List['A_RECHERCHE']] = relationship('A_RECHERCHE', uselist=True, back_populates='RECHERCHE_')

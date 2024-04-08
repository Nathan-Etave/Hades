from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from app.extensions import db


class RECHERCHE(db.Model):
    __tablename__ = 'RECHERCHE'

    champ_Recherche = mapped_column(String(255), primary_key=True)

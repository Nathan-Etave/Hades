from typing import List
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.extensions import db

class ROLE(db.Model):
    __tablename__ = 'ROLE'

    id_Role = mapped_column(Integer, primary_key=True)
    nom_Role = mapped_column(String(255))


from typing import List
from sqlalchemy import String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.extensions import db

class TAG(db.Model):
    __tablename__ = 'TAG'

    nom_Tag = mapped_column(String(255), primary_key=True)
    
    A_TAG: Mapped[List['A_TAG']] = relationship('A_TAG', uselist=True, back_populates='TAG_')

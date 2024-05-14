from typing import Optional
from sqlalchemy import DateTime, ForeignKeyConstraint, Integer, String, Text, Index, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.extensions import db

class LIEN(db.Model):
    __tablename__ = 'LIEN'
    __table_args__ = (
        ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_Lien_Utilisateur'),
        Index('fk_Lien_Utilisateur', 'id_Utilisateur')
    )
    
    id_Lien = mapped_column(Integer, primary_key=True)
    nom_Lien = mapped_column(String(255))
    lien_Lien = mapped_column(String(255))
    description_Lien = mapped_column(Text)
    date_Lien = mapped_column(DateTime, default=db.func.current_timestamp())
    id_Utilisateur = mapped_column(UUID(as_uuid=True))

    UTILISATEUR: Mapped[Optional['UTILISATEUR']] = relationship('UTILISATEUR', back_populates='LIEN')
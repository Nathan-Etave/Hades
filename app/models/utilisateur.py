import uuid
from typing import List, Optional
from sqlalchemy import Index, Integer, String, ForeignKeyConstraint, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.extensions import db
from flask_login import UserMixin

class UTILISATEUR(db.Model, UserMixin):
    __tablename__ = 'UTILISATEUR'
    __table_args__ = (
        ForeignKeyConstraint(['id_Role'], ['ROLE.id_Role'], name='fk_Utilisateur_Role'),
        Index('fk_Utilisateur_Role', 'id_Role')
    )

    id_Utilisateur = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_Utilisateur = mapped_column(String(255))
    prenom_Utilisateur = mapped_column(String(255))
    email_Utilisateur = mapped_column(String(255))
    mdp_Utilisateur = mapped_column(String(255))
    telephone_Utilisateur = mapped_column(String(255))
    est_Actif_Utilisateur = mapped_column(Integer)
    id_Role = mapped_column(Integer)

    def get_id(self):
        return self.id_Utilisateur
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def to_dict_secure(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in ['email_Utilisateur', 'mdp_Utilisateur', 'telephone_Utilisateur']}
    
    def is_admin(self):
        return self.id_Role != 4

    FICHIER_: Mapped[List['FICHIER']] = relationship('FICHIER', secondary='FAVORIS', back_populates='UTILISATEUR_')
    ROLE_: Mapped[Optional['ROLE']] = relationship('ROLE', back_populates='UTILISATEUR')
    A_RECHERCHE: Mapped[List['A_RECHERCHE']] = relationship('A_RECHERCHE', uselist=True, back_populates='UTILISATEUR_')
    NOTIFICATION: Mapped[List['NOTIFICATION']] = relationship('NOTIFICATION', uselist=True, back_populates='UTILISATEUR_')
    LIEN: Mapped[List['LIEN']] = relationship('LIEN', uselist=True, back_populates='UTILISATEUR')
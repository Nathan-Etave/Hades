from sqlalchemy import Integer, String, ForeignKeyConstraint, Index
from sqlalchemy.orm import mapped_column, Mapped
from app.extensions import db

class FICHIER(db.Model):
    __tablename__ = 'FICHIER'
    __table_args__ = (
        ForeignKeyConstraint(['id_Dossier'], ['DOSSIER.id_Dossier'], name='fk_Fichier_Dossier'),
        Index('fk_Fichier_Dossier', 'id_Dossier')
    )

    id_Fichier = mapped_column(Integer, primary_key=True)
    id_Dossier = mapped_column(Integer)
    URI_Fichier = mapped_column(String(255))

    DOSSIER_: Mapped[Optional['DOSSIER']] = relationship('DOSSIER', back_populates='FICHIER')
    UTILISATEUR_: Mapped[List['UTILISATEUR']] = relationship('UTILISATEUR', secondary='FAVORIS', back_populates='FICHIER_')
    A_TAG: Mapped[List['A_TAG']] = relationship('A_TAG', uselist=True, back_populates='FICHIER_')
    NOTIFICATION: Mapped[List['NOTIFICATION']] = relationship('NOTIFICATION', uselist=True, back_populates='FICHIER_')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


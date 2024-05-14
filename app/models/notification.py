from sqlalchemy import Integer, DateTime, Index, ForeignKeyConstraint, UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import Optional
from app.extensions import db


class NOTIFICATION(db.Model):
    __tablename__ = 'NOTIFICATION'
    __table_args__ = (
        ForeignKeyConstraint(['id_Fichier'], ['FICHIER.id_Fichier'], name='fk_Notification_Fichier'),
        ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_Notification_Utilisateur'),
        Index('fk_Notification_Fichier', 'id_Fichier'),
        Index('fk_Notification_Utilisateur', 'id_Utilisateur')
    )

    id_Notification = mapped_column(Integer, primary_key=True)
    datetime_Notification = mapped_column(DateTime)
    type_Notification = mapped_column(Integer)
    id_Utilisateur = mapped_column(UUID(as_uuid=True))
    id_Fichier = mapped_column(Integer)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    FICHIER_: Mapped[Optional['FICHIER']] = relationship('FICHIER', back_populates='NOTIFICATION')
    UTILISATEUR_: Mapped[Optional['UTILISATEUR']] = relationship('UTILISATEUR', back_populates='NOTIFICATION')
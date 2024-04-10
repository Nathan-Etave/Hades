from sqlalchemy import Integer, String, ForeignKeyConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.extensions import db

class A_TAG(db.Model):
    __tablename__ = 'A_TAG'
    __table_args__ = (
        ForeignKeyConstraint(['id_Fichier'], ['FICHIER.id_Fichier'], name='fk_A_Tag_Fichier'),
        ForeignKeyConstraint(['nom_Tag'], ['TAG.nom_Tag'], name='fk_A_Tag_Tag'),
        Index('fk_A_Tag_Tag', 'nom_Tag')
    )

    id_Fichier = mapped_column(Integer, primary_key=True, nullable=False)
    nom_Tag = mapped_column(String(255), primary_key=True, nullable=False)
    nb_Occurrence = mapped_column(Integer)

    FICHIER_: Mapped['FICHIER'] = relationship('FICHIER', back_populates='A_TAG')
    TAG_: Mapped['TAG'] = relationship('TAG', back_populates='A_TAG')
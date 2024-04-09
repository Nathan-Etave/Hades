from sqlalchemy import DateTime, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.extensions import db

class A_RECHERCHE(db.Model):
    __tablename__ = 'A_RECHERCHE'
    __table_args__ = (
        ForeignKeyConstraint(['champ_Recherche'], ['RECHERCHE.champ_Recherche'], name='fk_A_Recherche_Recherche'),
        ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_A_Recherche_Utilisateur'),
        Index('fk_A_Recherche_Recherche', 'champ_Recherche')
    )

    id_Utilisateur = mapped_column(Integer, primary_key=True, nullable=False)
    champ_Recherche = mapped_column(String(255), primary_key=True, nullable=False)
    datetime_Recherche = mapped_column(DateTime, primary_key=True, nullable=False)

    RECHERCHE_: Mapped['RECHERCHE'] = relationship('RECHERCHE', back_populates='A_RECHERCHE')
    UTILISATEUR_: Mapped['UTILISATEUR'] = relationship('UTILISATEUR', back_populates='A_RECHERCHE')

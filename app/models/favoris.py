from sqlalchemy import Table, Column, Integer, ForeignKeyConstraint, Index
from app.extensions import db

FAVORIS = Table(
    'FAVORIS', db.Model.metadata,
    Column('id_Utilisateur', Integer, primary_key=True, nullable=False),
    Column('id_Fichier', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['id_Fichier'], ['FICHIER.id_Fichier'], name='fk_Favoris_Fichier'),
    ForeignKeyConstraint(['id_Utilisateur'], ['UTILISATEUR.id_Utilisateur'], name='fk_Favoris_Utilisateur'),
    Index('fk_Favoris_Fichier', 'id_Fichier')
)

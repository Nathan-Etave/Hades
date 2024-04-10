from sqlalchemy import Table, Column, Integer, ForeignKeyConstraint, Index
from app.extensions import db

SOUS_DOSSIER = Table(
    'SOUS_DOSSIER', db.Model.metadata,
    Column('id_Dossier_Parent', Integer, primary_key=True, nullable=False),
    Column('id_Dossier_Enfant', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['id_Dossier_Enfant'], ['DOSSIER.id_Dossier'], name='fk_Sous_Dossier_Enfant'),
    ForeignKeyConstraint(['id_Dossier_Parent'], ['DOSSIER.id_Dossier'], name='fk_Sous_Dossier_Parent'),
    Index('fk_Sous_Dossier_Enfant', 'id_Dossier_Enfant')
)
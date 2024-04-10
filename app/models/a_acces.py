from sqlalchemy import Table, Column, Integer, ForeignKeyConstraint, Index
from app.extensions import db

A_ACCES = Table(
    'A_ACCES', db.Model.metadata,
    Column('id_Role', Integer, primary_key=True, nullable=False),
    Column('id_Dossier', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['id_Dossier'], ['DOSSIER.id_Dossier'], name='fk_A_Acces_Dossier'),
    ForeignKeyConstraint(['id_Role'], ['ROLE.id_Role'], name='fk_A_Acces_Role'),
    Index('fk_A_Acces_Dossier', 'id_Dossier')
)
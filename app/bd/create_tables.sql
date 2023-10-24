create table ETAT_FICHIER(
    idEtatFichier int,
    nomEtatFichier varchar(255),
    descriptionEtatFichier varchar(255),
    primary key (idEtatFichier)
)ENGINE=InnoDB;

create table CATEGORIE(
    idCategorie int,
    nomCategorie varchar(255),
    primary key (idCategorie) 
)ENGINE=InnoDB;

create table SOUS_CATEGORIE(
    idSousCategorie int,
    nomSousCategorie varchar(255),
    idCategorie int,
    primary key (idSousCategorie),
    constraint FKsous_categorie_categorie foreign key (idCategorie) references CATEGORIE(idCategorie)

)ENGINE=InnoDB;

create table FICHIER(
    idFichier int,
    nomFichier varchar(255),
    leFichier longblob,
    extensionfichier varchar(255),
    idSousCategorie int,
    primary key (idFichier),
    constraint FKfichier_sousCategorie foreign key (idSousCategorie) references SOUS_CATEGORIE(idSousCategorie)
)ENGINE=InnoDB;

create table EST_ETAT(
    idFichier int,
    idEtatFichier int,
    primary key (idFichier, idEtatFichier),
    constraint FKest_etat_fichier foreign key (idFichier) references FICHIER(idFichier),
    constraint FKest_etat_etat foreign key (idEtatFichier) references ETAT_FICHIER(idEtatFichier)
)ENGINE=InnoDB;

create table ROLE_POMPIER(
    idRole int,
    nomRole varchar(255),
    descriptionRole varchar(255),
    primary key (idRole)
)ENGINE=InnoDB;

create table POMPIER(
    idPompier int,
    nomPompier varchar(255),
    prenomPompier varchar(255),
    emailPompier varchar(255),
    mdpPompier varchar(255),
    photoPompier longblob,
    idRole int,
    primary key (idPompier),
    constraint FKpompier_rolePompier foreign key (idRole) references ROLE_POMPIER(idRole)
)ENGINE=InnoDB;

create table DATE(
    idDate int,
    laDate date,
    primary key (idDate)
)ENGINE=InnoDB;

create table A_CONSULTE(
    idFichier int,
    idPompier int,
    idDate int,
    primary key (idFichier, idPompier,idDate),
    constraint FKa_consulte_fichier foreign key (idFichier) references FICHIER(idFichier),
    constraint FKa_consulte_pompier foreign key (idPompier) references POMPIER(idPompier),
    constraint FKa_consulte_date foreign key (idDate) references DATE(idDate)
)ENGINE=InnoDB;

create table FAVORI(
    idFichier int,
    idPompier int,
    primary key (idFichier, idPompier),
    constraint FKfavori_pompier foreign key (idPompier) references POMPIER(idPompier),
    constraint FKfavori_fichier foreign key (idFichier) references FICHIER(idFichier)
    
)ENGINE=InnoDB;

create table SIGNALEMENT(
    idFichier int,
    idPompier int,
    descriptionSignalement varchar(255),
    primary key (idFichier, idPompier),
    constraint FKsignalement_fichier foreign key (idFichier) references FICHIER(idFichier),
    constraint FKsignalement_pompier foreign key (idPompier) references POMPIER(idPompier)
)ENGINE=InnoDB;










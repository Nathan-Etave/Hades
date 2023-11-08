create table TAG(
    nomTag varchar(255),
    primary key (nomTag)
)ENGINE=InnoDB;

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
    categorieParent int,
    categorieEnfant int,
    primary key (categorieEnfant, categorieParent),
    constraint FKcategorieEnfant_categorie foreign key (categorieEnfant) references CATEGORIE(idCategorie),
    constraint FKcategorieParent_categorie foreign key (categorieParent) references CATEGORIE(idCategorie)
    
)ENGINE=InnoDB;

create table FICHIER(
    idFichier int,
    nomFichier varchar(255),
    leFichier longblob,
    extensionfichier varchar(255),
    idEtatFichier int,
    primary key (idFichier),
    constraint FKfichier_etat foreign key (idEtatFichier) references ETAT_FICHIER(idEtatFichier)
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

create table EST_CAT(
    idCategorie int,
    idFichier int,
    primary key (idCategorie, idFichier),
    constraint FKest_Categorie foreign key (idCategorie) references CATEGORIE(idCategorie),
    constraint FKest_cat_fichier foreign key (idFichier) references FICHIER (idFichier)
)ENGINE=InnoDB;

create table A_TAG(
    nomTag varchar(255),
    idFichier int,
    primary key (nomTag,idFichier),
    constraint FKTag foreign key (nomTag) references TAG(nomTag),
    constraint FKtag_fic foreign key (idFichier) references FICHIER(idFichier)
)ENGINE=InnoDB;

create table NOTIFICATION(
    idNotification int,
    texteNotification varchar(255),
    typeChange varchar(255),
    raisonNotification varchar(255),
    primary key (idNotification)
)ENGINE=InnoDB;

create table A_NOTIFICATION(
    idNotification int,
    idPompier int,
    idFichier int,
    idDate int,
    primary key (idNotification, idPompier, idFichier, idDate),
    constraint FKnotif_pompier foreign key (idPompier) references POMPIER(idPompier),
    constraint FKnotif_notif foreign key (idNotification) references NOTIFICATION(idNotification),
    constraint FKnotif_fichier foreign key (idFichier) references FICHIER(idFichier),
    constraint FKnotif_date foreign key (idDate) references DATE(idDate)
)ENGINE=InnoDB;

create table HISTORIQUE(
    nouvelleVersion int,
    ancienVersion int,
    primary key (nouvelleVersion, ancienVersion),
    constraint FKnouvelleVersion_fichier foreign key (nouvelleVersion) references FICHIER(idFichier),
    constraint FKancienVersion_fichier foreign key (ancienVersion) references FICHIER(idFichier)
)ENGINE=InnoDB;

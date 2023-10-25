-- INSERT INTO FICHIER (idFichier, nomFichier, leFichier, extensionfichier, idSousCategorie)VALUES
--     (1, 'mon_fichier.pdf', null, 'pdf', 1);




-- INSERT INTO TAG(nomTag) VALUE


-- INSERT INTO A_TAG(nomTag, idFichier) VALUES

-- INSERT INTO NOTIFICATION(idNotification, texteNotification) VALUES

-- INSERT INTO A_NOTIFICATION(idNotification, idPompier) VALUES

-- INSERT INTO HISTORIQUE(nouvelleVersion, ancienVersion) VALUES

-- INSERT INTO EST_CAT(idCategorie, idFichier) VALUES


INSERT INTO CATEGORIE (idCategorie, nomCategorie) VALUES
    (1, 'Incendie'),
    (2, 'Accident'),
    (3, 'Inondation'),
    (4, 'Chimique'),
    (5, 'Nucléaire'),
    (6, 'Terrorisme'),
    (7, 'Tremblement de terre'),
    (8, 'Noyade'),
    (9, 'Maladies'),
    (10, 'Feu de maison'),
    (11, 'Feu de forêt'),
    (12, 'Feu de voiture'),
    (13, 'Feu de poubelle'),
    (14, 'Feu de cheminée'),
    (15, 'Feu de brousse'),
    (16, 'Feu de cave'),
    (17, 'Feu de toiture'),
    (18, 'Feu de cheminée'),
    (19, 'Accident de voiture'),
    (20, 'Accident de train'),
    (21, 'Accident de bateau'),
    (22, 'Accident d''avion'),
    (23, 'Grande'),
    (24, 'Moyenne'),
    (25, 'Petite'),
    (26, 'Bombe'),
    (27, 'Arme'),
    (28, 'Tsunami'), 
    (29, 'Virus'),
    (30, 'Épidémie'),
    (31, 'Virale'),
    (32, 'Sauvage'),
    (33, 'Domestique'),
    (34, 'Serpent'),
    (35, 'Animaux');



INSERT INTO ROLE_POMPIER (idRole, nomRole, descriptionRole) VALUES
    (1, 'Capitaine', 'Capitaine de la caserne'),
    (2, 'Lieutenant', 'Lieutenant de la caserne'),
    (3, 'Sergent', 'Sergent de la caserne'),
    (4, 'Sapeur', 'Sapeur de la caserne'),
    (5, 'Admin', "Administrateur de l'application");

INSERT INTO POMPIER (idPompier, nomPompier, prenomPompier, emailPompier, mdpPompier, photoPompier, idRole) VALUES
    (1, 'Dupont', 'Jean', 'jean.dupont@gmail.com', '123456', null, 1),
    (2, 'Durand', 'Pierre', 'pierre.durand@gmail.com', '123456', null, 2),
    (3, 'Martin', 'Paul', 'paul.martin@gmail.com', '123456', null, 3),
    (4, 'Dubois', 'Jacques', 'jacques.dubois@gmail.com', '123456', null, 4),
    (5, 'Lefebvre', 'Pierre', 'pierre.lefebvre@gmail.com', '123456', null, 5);


INSERT INTO FICHIER (idFichier, nomFichier, leFichier, extensionfichier, idEtatFichier) VALUES
    (1, 'mon_fichier.pdf', null, 'pdf', 1),
    (2, 'mon_fichier2.pdf', null, 'pdf', 2),
    (3, 'mon_fichier3.pdf', null, 'pdf', 3),
    (4, 'mon_fichier4.pdf', null, 'pdf', 2),
    (5, 'mon_fichier5.pdf', null, 'pdf', 1),
    (6, 'mon_fichier6.pdf', null, 'pdf', 3),
    (7, 'mon_fichier7.pdf', null, 'pdf', 2),
    (8, 'mon_fichier8.pdf', null, 'pdf', 2),
    (9, 'mon_fichier9.pdf', null, 'pdf', 3),
    (10, 'mon_fichier10.pdf', null, 'pdf', 1);

INSERT INTO ETAT_FICHIER (idEtatFichier, nomEtatFichier, descriptionEtatFichier) VALUES
    (1, 'Ancienne version', 'Ancienne version du fichier'),
    (2, 'Nouvelle version', 'Nouvelle version du fichier'),
    (3, 'Non classifié', 'Le fichier est non classifié');

INSERT INTO SIGNALEMENT (idFichier, idPompier, descriptionSignalement) VALUES
    (1, 1, 'Titre incompatible avec le contenu du fichier.'),
    (2, 2, 'Ce fichier ne devrait pas être accessible à tous.'),
    (3, 3, 'Ce fichier est une ancienne version.'),
    (4, 4, 'Ce fichier est une nouvelle version.'),
    (5, 5, 'Ce fichier est non classifié.'),
    (6, 1, "Ce fichier n'est pas rangé au bon endroit."),
    (7, 2, 'Le fichier est corrompu.'),
    (8, 3, "Il y a plein de fautes d'orthographe."),
    (9, 4, 'Le fichier est trop volumineux.'),
    (10, 5, 'Le fichier est trop petit.');

INSERT INTO FAVORI (idFichier, idPompier) VALUES
    (1,1),
    (1,2),
    (2,3),
    (3,3),
    (4,4),
    (5,5),
    (6,1),
    (7,2),
    (8,3),
    (9,4),
    (10,5);

INSERT INTO DATE(idDate, laDate) VALUES
    (1, '2019-01-01'),
    (2, '2019-01-02'),
    (3, '2019-01-03'),
    (4, '2019-01-04'),
    (5, '2019-01-05'),
    (6, '2019-01-06'),
    (7, '2019-01-07'),
    (8, '2019-01-08'),
    (9, '2019-01-09'),
    (10, '2019-01-10');

INSERT INTO A_CONSULTE(idFichier, idPompier, idDate) VALUES
    (1, 1, 1),
    (1, 4, 1),
    (1, 2, 10),
    (10, 2, 10),
    (8, 3, 10),
    (9, 4, 10),
    (7, 5, 10),
    (6, 1, 10),
    (5, 2, 10),
    (4, 3, 10),
    (3, 4, 10),
    (2, 5, 10);

INSERT INTO SOUS_CATEGORIE(categorieParent, categorieEnfant) VALUES
    (1, 10),
    (1, 11),
    (1, 12),
    (1, 13),
    (1, 14),
    (1, 15),
    (1, 16),
    (1, 17),
    (1, 18);
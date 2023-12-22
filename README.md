# <u>Pinpon 45</u>

## <u>Sommaire</u>

- [Pinpon 45](#pinpon-45)
  - [Sommaire](#sommaire)
  - [Présentation](#présentation)
  - [Installation](#installation)
    - [Prérequis](#prérequis)
    - [Exécution de l'application](#exécution-de-lapplication)
  - [Se connecter à l'application](#se-connecter-à-lapplication)
    - [Comptes de test](#comptes-de-test)
  - [Structure de l'application](#structure-de-lapplication)
    - [Répertoire `app`](#répertoire-app)
    - [Répertoire `app/static`](#répertoire-appstatic)
    - [Répertoire `app/templates`](#répertoire-apptemplates)
    - [Répertoire `database`](#répertoire-database)
    - [Répertoire `docs`](#répertoire-docs)
  - [Équipe de développement](#équipe-de-développement)

## <u>Présentation</u>

PinPon45 est une application web permettant la gestion efficace des documentations techniques et réglementaires exploitables avec facilité par les sapeurs-pompiers du Loiret.
L'application permet une interrogation rapide et exhaustive des documents par mots-clés (tags), par catégories, par type de document, par favoris, par date consultation, etc.
Les documents sont stockés sur une base de données locale au serveur, et sont accessibles depuis l'application web. Les documents y sont centralisés, historisés et consultables par les utilisateurs autorisés.

## <u>Installation</u>

### Prérequis

- Python 3.10 ou supérieur
- pip
- virtualenv (optionnel mais recommandé, peut être installé avec pip : `pip install virtualenv`)
- git

### Exécution de l'application

- Pour installer l'applicaion, il suffit de cloner le dépôt git et de se placer dans le répertoire de l'application :

    ```bash
    git clone https://github.com/Nathan-Etave/PinPon45.git
    cd PinPon45
    ```

- Pour créer un environnement virtuel, permettant d'isoler les dépendances de l'application, il suffit de lancer la commande suivante (optionnel) :

    ```bash
    virtualenv -p python3 env
    ```

- Pour activer l'environnement virtuel, il suffit de lancer la commande suivante :

    ```bash
    source env/bin/activate # Linux
    # ou
    env\Scripts\activate # Windows
    ```

- Pour installer les dépendances nécessaires a l'application, il suffit de lancer la commande suivante (l'installation peut prendre quelques minutes) :

    ```bash
    pip install -r requirements.txt
    ```

- **IMPORTANT !**  Avant de lancer l'application, il faut déclarer une clé secrète pour l'application et créer la base de données :

    Pour déclarer la clé secrète, il faut se rendre dans le fichier `PinPon45/app/__init__.py` et modifier la ligne suivante :

    ```python
    app.config['SECRET_KEY'] = '' # Modifier la valeur entre les guillemets
    ```

- Pour créer la base de données, il faut lancer la commande suivante (la base de données sera prérémplie avec des données de test disponibles dans le fichier `PinPon45/app/static/csv/`):

    ```bash
    flask init_database # Linux
    # ou
    flask --app app init_database # Windows
    ```
    Il est essentielle de garder les rôles "Administrateur" et "Désactivé" dans une version de production.
    Il est également essentiel de garder la catégorie "Non catégorisé" dans une version de production.

- Enfin, pour lancer l'application, il suffit de lancer la commande suivante :

    ```bash
    flask run --host=<ip> --port=<port> # Linux
    # ou
    flask --app app run --host=<ip> --port=<port> # Windows
    ```
    L'application est maintenant accessible depuis un navigateur web à l'adresse `http://<ip>:<port>`.

## <u>Se connecter à l'application</u>

Pour se connecter à l'application, il faut se rendre sur l'adresse `http://<ip>:<port>/login` et entrer les identifiants d'un compte utilisateur.

### Comptes de test

Différents comptes de test sont disponibles pour tester l'application :

| Identifiant | Mot de passe | Rôle |
| ----------- | ------------ | ---- |
| admin@sdis45.fr       | admin        | Administrateur |
| michel.lapompe@gmail.com | michel | Utilisateur |
| marguerite.pompator@gmail.com | marguerite | Utilisateur |


## <u>Structure de l'application</u>

### Répertoire `app`

- Le répertoire `app` contient l'ensemble des fichiers python nécessaires au fonctionnement de l'application.
- Le fichier `__init__.py` permet d'initialiser l'application et de définir les variables d'environnement.
- Le fichier `database.py` permet de créer les tables de la base de données.
- Le fichier `forms.py` permet de créer les formulaires de l'application.
- Le fichier `models.py` permet de définir la structure de la base de données.
- Le fichier `nlp.py` permet de générer les tags automatiquement grâce à un algorithme de NLP.
- Le fichier `requests.py` permet de définir les requêtes à la base de données.
- Le fichier `view.py` permet de définir les routes de l'application.

### Répertoire `app/static`

- Le répertoire `app/static` contient l'ensemble des fichiers statiques de l'application.
- Le répertoire `app/static/css` contient l'ensemble des fichiers css de l'application.
- Le répertoire `app/static/csv` contient l'ensemble des fichiers csv de l'application.
- Le répertoire `app/static/js` contient l'ensemble des fichiers JavaScript de l'application.
- Le répertoire `app/static/temp` contient l'ensemble des fichiers temporaires de l'application (celui-ci est créé automatiquement lorsque nécessaire).

### Répertoire `app/templates`

- Le répertoire `app/templates` contient l'ensemble des fichiers html de l'application.
- Le répertoire `app/templates/components` contient l'ensemble des fichiers html de composants de l'application.

### Répertoire `database`

- Le répertoire `database` contient le fichier de la base de données de l'application.

### Répertoire `docs`

- Le répertoire `docs` contient l'ensemble des documents de conception de l'application.

## <u>Équipe de développement</u>

- Nathan Etave ([GitHub](https://github.com/Nathan-Etave))
- Romain Mechain ([GitHub](https://github.com/RomainMechain))
- Louis Lebeaupin ([GitHub](https://github.com/LouisL18))
- Arthur Villette ([GitHub](https://github.com/ArthurVillette))
- Hugo Sainson ([GitHub](https://github.com/Norikokonut))
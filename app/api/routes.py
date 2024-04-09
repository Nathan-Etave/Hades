from app import db
from app.models.fichier import FICHIER
from app.models.dossier import DOSSIER
from app.models.tag import TAG
from app.models.a_tag import A_TAG
from app.models.utilisateur import UTILISATEUR
from app.models.favoris import FAVORIS
from app.models.notification import NOTIFICATION
from flask import jsonify, request
from app.api import bp
from sqlalchemy.orm import sessionmaker
from unidecode import unidecode

# --------------------------------------------Fichier--------------------------------------------

# -----GET-----

@bp.route('/fichier/<int:id>', methods=['GET'])
def get_fichier(id):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    fichier = session.query(FICHIER).filter(FICHIER.id_Fichier == id).first()
    session.close()
    if fichier is None:
        return jsonify({'error': 'fichier not found'}), 404
    return jsonify(fichier.to_dict())


@bp.route('/fichiers', methods=['GET'])
def get_fichiers():
    data = FICHIER.query.all()
    return jsonify([fichier.to_dict() for fichier in data])

# -----POST-----

@bp.route('/fichier', methods=['POST'])
def add_fichier() :
    uri = request.json.get('uri')
    tags = request.json.get('tags')
    id_dossier = request.json.get('id_dossier')
    file = FICHIER(URI_Fichier=uri, id_Dossier=id_dossier)
    db.session.add(file)
    db.session.commit()
    for tag in tags :
        if not TAG.query.filter_by(nom_Tag=unidecode(tag[0].lower())).first():
            new_tag = TAG(nom_Tag=unidecode(tag[0].lower()))
            db.session.add(new_tag)
            db.session.commit()
        a_tag = A_TAG(id_Fichier=file.id_Fichier, nom_Tag=unidecode(tag[0].lower()), nb_Occurrence=tag[1])
        db.session.add(a_tag)
        db.session.commit()
    return jsonify(file.to_dict())

# -----PATCH-----

@bp.route('/fichier/<int:id>', methods=['PATCH'])
def update_fichier(id):
    uri = request.json.get('uri')
    tags = request.json.get('tags')
    id_dossier = request.json.get('id_dossier')
    file = FICHIER.query.filter_by(id_Fichier=id).first()
    if file is None:
        return jsonify({'error': 'file not found'}), 404
    if uri is not None:
        file.URI_Fichier = uri
    if id_dossier is not None:
        file.id_Dossier = id_dossier
    if tags is not None:
        db.session.execute(A_TAG.delete().where(A_TAG.c.id_Fichier == id))
    db.session.commit()
    for tag in tags :
        if not TAG.query.filter_by(nom_Tag=unidecode(tag[0].lower())).first():
            new_tag = TAG(nom_Tag=unidecode(tag[0].lower()))
            db.session.add(new_tag)
            db.session.commit()
        a_tag = A_TAG(id_Fichier=file.id_Fichier, nom_Tag=unidecode(tag[0].lower()), nb_Occurrence=tag[1])
        db.session.add(a_tag)
        db.session.commit()
    return jsonify(file.to_dict())

# --------------------------------------------Dosssier--------------------------------------------

# -----PATCH-----

@bp.route('/dossier/<int:id_dossier>', methods=['PATCH'])
def update_dossier(id_dossier):
    name = request.json.get('name')
    color = request.json.get('color')
    priority = request.json.get('priority')
    dossier = DOSSIER.query.filter_by(id_Dossier=id_dossier).first()
    if dossier is None:
        return jsonify({'error': 'DOSSIER not found'}), 404
    if name is not None:
        dossier.nom_Dossier = name
    if color is not None:
        dossier.couleur_Dossier = color
    if priority is not None:
        dossier.priorite_Dossier = priority
    db.session.commit()
    return jsonify(dossier.to_dict())

# --------------------------------------------Utilisateur--------------------------------------------

# -----POST-----

@bp.route('/utilisateur', methods=['POST'])
def add_useur() :
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')
    role = request.json.get('role')
    actif = request.json.get('actif')
    user = UTILISATEUR(nom_Utilisateur=last_name, prenom_Utilisateur=first_name, email_Utilisateur=email, mdp_Utilisateur=password, telephone_Utilisateur=phone, id_Role=role, est_Actif_Utilisateur=actif)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict())

# -----PATCH-----

@bp.route('/utilisateur/<int:id>', methods=['PATCH'])
def update_user(id):
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    email = request.json.get('email')
    phone = request.json.get('phone')
    password = request.json.get('password')
    role = request.json.get('role')
    actif = request.json.get('actif')
    user = UTILISATEUR.query.filter_by(id_Utilisateur=id).first()
    if user is None:
        return jsonify({'error': 'user not found'}), 404
    if first_name is not None:
        user.prenom_Utilisateur = first_name
    if last_name is not None:
        user.nom_Utilisateur = last_name
    if email is not None:
        user.email_Utilisateur = email
    if phone is not None:
        user.telephone_Utilisateur = phone
    if password is not None:
        user.mdp_Utilisateur = password
    if role is not None:
        user.id_Role = role
    if actif is not None:
        user.est_Actif_Utilisateur = actif
    db.session.commit()
    return jsonify(user.to_dict())

# ----------Favoris----------

# -----DELETE-----

@bp.route('/utilisateur/<int:id>/favoris', methods=['DELETE'])
def unfavorite_file(id):
    file_id = request.json.get('file_id')
    user = UTILISATEUR.query.filter_by(id_Utilisateur=id).first()
    if user is None:
        return jsonify({'error': 'user not found'}), 404
    file = FICHIER.query.filter_by(id_Fichier=file_id).first()
    if file is None:
        return jsonify({'error': 'file not found'}), 404
    db.session.execute(FAVORIS.delete().where(FAVORIS.c.id_Utilisateur == id).where(FAVORIS.c.id_Fichier == file_id))
    db.session.commit()
    return jsonify(user.to_dict())

# -----POST-----

@bp.route('/utilisateur/<int:id>/favoris', methods=['POST'])
def favorite_file(id):
    file_id = request.json.get('file_id')
    user = UTILISATEUR.query.filter_by(id_Utilisateur=id).first()
    if user is None:
        return jsonify({'error': 'user not found'}), 404
    file = FICHIER.query.filter_by(id_Fichier=file_id).first()
    if file is None:
        return jsonify({'error': 'file not found'}), 404
    new_favorite = FAVORIS.insert().values(id_Utilisateur=id, id_Fichier=file_id)
    db.session.execute(new_favorite)
    db.session.commit()
    return jsonify(user.to_dict())

# ----------Notification----------

# -----DELETE-----

@bp.route('/utilisateur/<int:id>/notifications', methods=['DELETE'])
def delete_notification(id):
    notif_id = request.json.get('notif_id')
    user = UTILISATEUR.query.filter_by(id_Utilisateur=id).first()
    if user is None:
        return jsonify({'error': 'user not found'}), 404
    notif = NOTIFICATION.query.filter_by(id_Notification=notif_id).first()
    if notif is None:
        return jsonify({'error': 'notification not found'}), 404
    db.session.delete(notif)
    db.session.commit()
    return jsonify(user.to_dict())

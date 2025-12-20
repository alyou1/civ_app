from src.models import db, User, Role
from flask_jwt_extended import create_access_token, create_refresh_token, unset_jwt_cookies
from flask import jsonify, session
from datetime import datetime


def login_user(matricule, password):
    try:
        # Rechercher l'utilisateur
        user = User.query.filter_by(user_matricule=matricule).first()

        if not user:
            return {'error': 'matricule ou mot de passe incorrect'}, 401

        if not user.is_active:
            return {'error': 'Ce compte a été désactivé'}, 403

        if not user.check_password(password):
            return {'error': 'matricule ou mot de passe incorrect'}, 401

        # Mettre à jour la dernière connexion
        user.last_connection_date = datetime.now()
        db.session.commit()

        additional_claims = {
            'email': user.user_email,
            'roles': [role.role_name for role in user.roles],
            'user_name': user.full_name

        }
        access_token = create_access_token(
            identity=user.user_matricule,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=user.user_id)

        return {
            'message': 'Connexion réussie',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_claims': {
                'user_name': user.full_name,
                'email': user.user_email,
                'matricule': user.user_matricule,
                'roles': [role.role_name for role in user.roles]
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        return {'error': f'Erreur lors de la connexion: {str(e)}'}, 500


def logout_user():
    """
    Déconnecte un utilisateur (JWT est stateless, donc juste un message)
    :return: dict avec message de succès
    """
    response = jsonify({"logout":True})
    unset_jwt_cookies(response)
    session.clear()
    return response

def change_user_password(matricule, old_password, new_password):
    """
    Change le mot de passe d'un utilisateur
    :param matricule: ID de l'utilisateur
    :param old_password: Ancien mot de passe
    :param new_password: Nouveau mot de passe
    :return: dict avec message, status code
    """
    try:
        user = User.query.filter_by(user_matricule=matricule).first()

        if not user:
            return {'error': 'Utilisateur non trouvé'}, 404

        if not user.check_password(old_password):
            return {'error': 'Ancien mot de passe incorrect'}, 400

        if user.check_password(new_password):
            return {'error': 'Le nouveau mot de passe doit être différent'}, 400

        user.set_password(new_password)
        db.session.commit()

        return {'message': 'Mot de passe modifié avec succès'}, 200

    except Exception as e:
        db.session.rollback()
        return {'error': f'Erreur lors du changement: {str(e)}'}, 500

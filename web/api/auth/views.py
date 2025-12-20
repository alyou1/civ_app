from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from web.api.auth.functions import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Body: {
        "matricule": "0000",
        "password": "password123"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Aucune donnée fournie'}), 400

    matricule = data.get('matricule')
    password = data.get('password')

    if not matricule or not password:
        return jsonify({'error': 'Matricule et mot de passe requis'}), 400

    result, status = login_user(matricule, password)
    return jsonify(result), status


@auth_bp.route('/logout', methods=['GET'])
def logout():
    """
    POST /api/auth/logout
    Header: Authorization: Bearer <access_token>
    """
    response = logout_user()
    return response, 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    POST /api/auth/change-password
    Header: Authorization: Bearer <access_token>
    Body: {
        "matricule": "0000",
        "old_password": "OldPass123",
        "new_password": "NewPass456"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Aucune donnée fournie'}), 400

    matricule = data.get('matricule')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'error': 'Ancien et nouveau mot de passe requis'}), 400

    result, status = change_user_password(matricule, old_password, new_password)
    return jsonify(result), status


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    POST /api/auth/refresh
    Header: Authorization: Bearer <refresh_token>
    """
    from flask_jwt_extended import create_access_token
    from src.models import User

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_active:
        return jsonify({'error': 'Utilisateur non trouvé ou inactif'}), 404

    additional_claims = {
        'user_id': user.user_id,
        'email': user.user_email,
        'roles': [role.role_name for role in user.roles],
        'full_name': user.full_name
    }

    new_access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims
    )

    return jsonify({'access_token': new_access_token}), 200
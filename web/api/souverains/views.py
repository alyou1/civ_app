from flask import Blueprint, request, jsonify
from web.app import db
from web.models import Souverain
from datetime import datetime

souverain_bp = Blueprint('souverain', __name__, url_prefix='/api/souverains')

# Créer un souverain
@souverain_bp.route('/', methods=['POST'])
def create_souverain():
    try:
        data = request.get_json()
        
        if not data or 'nom_souverain' not in data:
            return jsonify({'error': 'Le nom du souverain est requis'}), 400
        
        # Vérifier si le souverain existe déjà
        if Souverain.query.filter_by(nom_souverain=data['nom_souverain']).first():
            return jsonify({'error': 'Ce souverain existe déjà'}), 409
        
        nouveau_souverain = Souverain(nom_souverain=data['nom_souverain'])
        db.session.add(nouveau_souverain)
        db.session.commit()
        
        return jsonify({
            'message': 'Souverain créé avec succès',
            'souverain': {
                'id_souverain': nouveau_souverain.id_souverain,
                'nom_souverain': nouveau_souverain.nom_souverain,
                'created_at': nouveau_souverain.created_at.isoformat() if nouveau_souverain.created_at else None
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Obtenir tous les souverains
@souverain_bp.route('/', methods=['GET'])
def get_souverains():
    try:
        # Exclure les souverains supprimés (soft delete)
        souverains = Souverain.query.filter(Souverain.deleted_at.is_(None)).all()
        
        return jsonify({
            'count': len(souverains),
            'souverains': [{
                'id_souverain': s.id_souverain,
                'nom_souverain': s.nom_souverain,
                'created_at': s.created_at.isoformat() if s.created_at else None,
                'updated_at': s.updated_at.isoformat() if s.updated_at else None
            } for s in souverains]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtenir un souverain par ID
@souverain_bp.route('/<int:id_souverain>', methods=['GET'])
def get_souverain(id_souverain):
    try:
        souverain = Souverain.query.filter_by(
            id_souverain=id_souverain,
            deleted_at=None
        ).first()
        
        if not souverain:
            return jsonify({'error': 'Souverain non trouvé'}), 404
        
        return jsonify({
            'id_souverain': souverain.id_souverain,
            'nom_souverain': souverain.nom_souverain,
            'created_at': souverain.created_at.isoformat() if souverain.created_at else None,
            'updated_at': souverain.updated_at.isoformat() if souverain.updated_at else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Modifier un souverain
@souverain_bp.route('/<int:id_souverain>', methods=['PUT'])
def update_souverain(id_souverain):
    try:
        souverain = Souverain.query.filter_by(
            id_souverain=id_souverain,
            deleted_at=None
        ).first()
        
        if not souverain:
            return jsonify({'error': 'Souverain non trouvé'}), 404
        
        data = request.get_json()
        
        if not data or 'nom_souverain' not in data:
            return jsonify({'error': 'Le nom du souverain est requis'}), 400
        
        # Vérifier si le nouveau nom existe déjà (pour un autre souverain)
        existing = Souverain.query.filter(
            Souverain.nom_souverain == data['nom_souverain'],
            Souverain.id_souverain != id_souverain
        ).first()
        
        if existing:
            return jsonify({'error': 'Ce nom de souverain existe déjà'}), 409
        
        souverain.nom_souverain = data['nom_souverain']
        souverain.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'Souverain modifié avec succès',
            'souverain': {
                'id_souverain': souverain.id_souverain,
                'nom_souverain': souverain.nom_souverain,
                'updated_at': souverain.updated_at.isoformat() if souverain.updated_at else None
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Supprimer un souverain (soft delete)
@souverain_bp.route('/<int:id_souverain>', methods=['DELETE'])
def delete_souverain(id_souverain):
    try:
        souverain = Souverain.query.filter_by(
            id_souverain=id_souverain,
            deleted_at=None
        ).first()
        
        if not souverain:
            return jsonify({'error': 'Souverain non trouvé'}), 404
        
        # Soft delete
        souverain.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'Souverain supprimé avec succès',
            'id_souverain': id_souverain
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, request, jsonify
from web.app import db
from web.models import Titre, Souverain
from datetime import datetime

titre_bp = Blueprint('titre', __name__, url_prefix='/api/titres')

# Créer un titre
@titre_bp.route('/', methods=['POST'])
def create_titre():
    try:
        data = request.get_json()
        
        # Validation des champs requis
        if not data or 'code_isin' not in data:
            return jsonify({'error': 'Le code ISIN est requis'}), 400
        
        if 'id_souverain' not in data:
            return jsonify({'error': 'L\'ID du souverain est requis'}), 400
        
        # Vérifier si le code ISIN existe déjà
        if Titre.query.filter_by(code_isin=data['code_isin']).first():
            return jsonify({'error': 'Ce code ISIN existe déjà'}), 409
        
        # Vérifier si le souverain existe
        souverain = Souverain.query.filter_by(
            id_souverain=data['id_souverain'],
            deleted_at=None
        ).first()
        
        if not souverain:
            return jsonify({'error': 'Souverain non trouvé'}), 404
        
        nouveau_titre = Titre(
            code_isin=data['code_isin'],
            id_souverain=data['id_souverain'],
            country=data.get('country')  # Optionnel
        )
        
        db.session.add(nouveau_titre)
        db.session.commit()
        
        return jsonify({
            'message': 'Titre créé avec succès',
            'titre': {
                'titre_id': nouveau_titre.titre_id,
                'code_isin': nouveau_titre.code_isin,
                'id_souverain': nouveau_titre.id_souverain,
                'nom_souverain': nouveau_titre.souverain.nom_souverain,
                'country': nouveau_titre.country,
                'created_at': nouveau_titre.created_at.isoformat() if nouveau_titre.created_at else None
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Obtenir tous les titres
@titre_bp.route('/', methods=['GET'])
def get_titres():
    try:
        # Paramètres de filtrage optionnels
        id_souverain = request.args.get('id_souverain', type=int)
        country = request.args.get('country')
        
        # Query de base
        query = Titre.query.filter(Titre.deleted_at.is_(None))
        
        # Filtres optionnels
        if id_souverain:
            query = query.filter_by(id_souverain=id_souverain)
        
        if country:
            query = query.filter_by(country=country)
        
        titres = query.all()
        
        return jsonify({
            'count': len(titres),
            'titres': [{
                'titre_id': t.titre_id,
                'code_isin': t.code_isin,
                'id_souverain': t.id_souverain,
                'nom_souverain': t.souverain.nom_souverain if t.souverain else None,
                'country': t.country,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'updated_at': t.updated_at.isoformat() if t.updated_at else None
            } for t in titres]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtenir un titre par ID
@titre_bp.route('/<int:titre_id>', methods=['GET'])
def get_titre(titre_id):
    try:
        titre = Titre.query.filter_by(
            titre_id=titre_id,
            deleted_at=None
        ).first()
        
        if not titre:
            return jsonify({'error': 'Titre non trouvé'}), 404
        
        return jsonify({
            'titre_id': titre.titre_id,
            'code_isin': titre.code_isin,
            'id_souverain': titre.id_souverain,
            'nom_souverain': titre.souverain.nom_souverain if titre.souverain else None,
            'country': titre.country,
            'created_at': titre.created_at.isoformat() if titre.created_at else None,
            'updated_at': titre.updated_at.isoformat() if titre.updated_at else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Obtenir tous les titres d'un souverain
@titre_bp.route('/souverain/<int:id_souverain>', methods=['GET'])
def get_titres_by_souverain(id_souverain):
    try:
        souverain = Souverain.query.filter_by(
            id_souverain=id_souverain,
            deleted_at=None
        ).first()
        
        if not souverain:
            return jsonify({'error': 'Souverain non trouvé'}), 404
        
        titres = Titre.query.filter_by(
            id_souverain=id_souverain,
            deleted_at=None
        ).all()
        
        return jsonify({
            'souverain': {
                'id_souverain': souverain.id_souverain,
                'nom_souverain': souverain.nom_souverain
            },
            'count': len(titres),
            'titres': [{
                'titre_id': t.titre_id,
                'code_isin': t.code_isin,
                'country': t.country,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'updated_at': t.updated_at.isoformat() if t.updated_at else None
            } for t in titres]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Modifier un titre
@titre_bp.route('/<int:titre_id>', methods=['PUT'])
def update_titre(titre_id):
    try:
        titre = Titre.query.filter_by(
            titre_id=titre_id,
            deleted_at=None
        ).first()
        
        if not titre:
            return jsonify({'error': 'Titre non trouvé'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        # Mise à jour du code ISIN
        if 'code_isin' in data:
            # Vérifier si le nouveau code ISIN existe déjà (pour un autre titre)
            existing = Titre.query.filter(
                Titre.code_isin == data['code_isin'],
                Titre.titre_id != titre_id
            ).first()
            
            if existing:
                return jsonify({'error': 'Ce code ISIN existe déjà'}), 409
            
            titre.code_isin = data['code_isin']
        
        # Mise à jour du souverain
        if 'id_souverain' in data:
            souverain = Souverain.query.filter_by(
                id_souverain=data['id_souverain'],
                deleted_at=None
            ).first()
            
            if not souverain:
                return jsonify({'error': 'Souverain non trouvé'}), 404
            
            titre.id_souverain = data['id_souverain']
        
        # Mise à jour du pays
        if 'country' in data:
            titre.country = data['country']
        
        titre.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'Titre modifié avec succès',
            'titre': {
                'titre_id': titre.titre_id,
                'code_isin': titre.code_isin,
                'id_souverain': titre.id_souverain,
                'nom_souverain': titre.souverain.nom_souverain if titre.souverain else None,
                'country': titre.country,
                'updated_at': titre.updated_at.isoformat() if titre.updated_at else None
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Supprimer un titre (soft delete)
@titre_bp.route('/<int:titre_id>', methods=['DELETE'])
def delete_titre(titre_id):
    try:
        titre = Titre.query.filter_by(
            titre_id=titre_id,
            deleted_at=None
        ).first()
        
        if not titre:
            return jsonify({'error': 'Titre non trouvé'}), 404
        
        # Soft delete
        titre.deleted_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'Titre supprimé avec succès',
            'titre_id': titre_id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

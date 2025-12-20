from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask import redirect, url_for, flash
from src.models import db, User, Role, Direction, UserRole
from wtforms import PasswordField
from werkzeug.security import generate_password_hash


class SecureAdminIndexView(AdminIndexView):
    """Page d'accueil personnalisée de l'admin avec protection"""

    @expose('/')
    def index(self):
        # Vérifier si l'utilisateur est connecté (optionnel pour l'instant)
        return super(SecureAdminIndexView, self).index()


class SecureModelView(ModelView):
    """Vue de base sécurisée pour tous les modèles"""

    # Protection CSRF
    form_base_class = SecureForm

    # Colonnes à ne pas afficher par défaut
    column_exclude_list = ['deleted_at', 'user_password']

    # Formulaire : champs à exclure
    form_excluded_columns = ['deleted_at', 'created_at', 'updated_at']

    # Pagination
    page_size = 20
    can_set_page_size = True

    # Filtres
    column_filters = ['created_at']

    # Export
    can_export = True
    export_types = ['csv', 'xls']

    def is_accessible(self):
        """
        Définit qui peut accéder à l'admin
        Pour l'instant, on laisse ouvert.
        Plus tard, vous pouvez ajouter une vérification JWT ici
        """
        # TODO: Ajouter vérification JWT et rôle Admin
        return True

    def inaccessible_callback(self, name, **kwargs):
        """Redirection si pas d'accès"""
        flash('Vous devez être administrateur pour accéder à cette page', 'error')
        return redirect(url_for('auth.login'))


class UserAdmin(SecureModelView):
    """Administration des utilisateurs"""

    # Colonnes à afficher dans la liste
    column_list = [
        'user_nom', 'user_prenom', 'user_email',
        'user_matricule' ,'direction', 'last_connection_date', 'created_at'
    ]

    # Colonnes searchable
    column_searchable_list = ['user_nom', 'user_prenom', 'user_email', 'user_matricule']

    # Filtres disponibles
    column_filters = ['user_email', 'direction.direction_name', 'created_at', 'direction']

    # Labels personnalisés
    column_labels = {
        'user_id': 'ID',
        'user_nom': 'Nom',
        'user_prenom': 'Prénom',
        'user_email': 'Email',
        'user_matricule': 'Matricule',
        'user_password': 'Mot de passe',
        'direction': 'Direction',
        'roles': 'Rôles',
        'last_connection_date': 'Dernière connexion',
        'created_at': 'Date de création',
        'updated_at': 'Date de modification'
    }
    # Champs du formulaire
    form_columns = [
        'user_nom', 'user_prenom', 'user_email',
        'user_matricule', 'user_password', 'direction', 'roles'
    ]

    # Exclure user_password du formulaire auto-généré
    form_excluded_columns = ['deleted_at', 'created_at', 'updated_at', 'last_connection_date']

    # Champs en lecture seule lors de l'édition
    form_widget_args = {
        'last_connection_date': {'readonly': True}
    }
    # Ajouter un champ mot de passe personnalisé
    form_extra_fields = {
        'password': PasswordField('Mot de passe')
    }

    def on_model_change(self, form, model, is_created):
        """Hook appelé avant la sauvegarde"""
        # Si le champ password personnalisé est rempli
        if hasattr(form, 'user_password') and form.user_password.data:
            model.user_password = generate_password_hash(form.user_password.data)
        # Si création et pas de mot de passe, définir un mot de passe par défaut
        elif is_created and not model.user_password:
            model.user_password = generate_password_hash('Password123')
            flash('Mot de passe par défaut défini: Password123', 'warning')

    def after_model_change(self, form, model, is_created):
        """Hook appelé après la sauvegarde"""
        action = "créé" if is_created else "modifié"

    # Formatage des colonnes
    def _format_roles(view, context, model, name):
        """Affiche les rôles de manière lisible"""
        if model.roles:
            return ', '.join([role.role_name for role in model.roles])
        return 'Aucun rôle'

    def on_model_delete(self, model):
        """Hook appelé avant la suppression"""
        from datetime import datetime
        model.deleted_at = datetime.now()
        db.session.add(model)

    column_formatters = {
        'roles': _format_roles
    }

    def delete_model(self, model):
        """Suppression réelle de l'utilisateur"""
        try:
            # Supprimer d'abord les associations UserRole
            UserRole.query.filter_by(user_id=model.user_id).delete()

            # Puis supprimer l'utilisateur
            db.session.delete(model)
            db.session.commit()

            flash(f'Utilisateur {model.full_name} supprimé avec succès!', 'success')
            return True
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la suppression: {str(e)}', 'error')
            return False


class RoleAdmin(SecureModelView):
    """Administration des rôles"""

    column_list = ['role_name', 'created_at']
    column_searchable_list = ['role_name']
    column_filters = ['role_name', 'created_at']

    column_labels = {
        'role_name': 'Nom du rôle',
        'created_at': 'Date de création',
        'users': 'Utilisateurs'
    }

    form_columns = ['role_name']

    def delete_model(self, model):
        """Soft delete du rôle"""
        try:
            from datetime import datetime
            model.deleted_at = datetime.now()

            # Soft delete des associations UserRole
            user_roles = UserRole.query.filter_by(role_id=model.role_id).all()
            for user_role in user_roles:
                user_role.deleted_at = datetime.now()

            db.session.commit()
            flash(f'Rôle {model.role_name} désactivé avec succès!', 'success')
            return True
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'error')
            return False



class DirectionAdmin(SecureModelView):
    """Administration des directions"""

    column_list = ['direction_name', 'created_at']
    column_searchable_list = ['direction_name']
    column_filters = ['direction_name', 'created_at']

    column_labels = {
        'direction_name': 'Nom de la direction',
        'created_at': 'Date de création',
        'users': 'Utilisateurs'
    }

    form_columns = ['direction_name']

    def delete_model(self, model):
        """Soft delete de la direction"""
        try:
            from datetime import datetime
            model.deleted_at = datetime.now()
            db.session.commit()
            flash(f'Direction {model.direction_name} désactivée avec succès!', 'success')
            return True
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'error')
            return False


class UserRoleAdmin(SecureModelView):
    """Administration des associations utilisateur-rôle"""

    column_list = ['user', 'role', 'created_at']

    column_labels = {
        'user': 'Utilisateur',
        'role': 'Rôle',
        'created_at': 'Assigné le'
    }

    form_columns = ['user_id','role_id']


def init_admin(app):
    """Initialise Flask-Admin avec l'application"""

    admin = Admin(
        app,
        name='Administration',
        template_mode='bootstrap4',
        index_view=SecureAdminIndexView(), # Template personnalisé (optionnel)
    )

    # Ajouter les vues de modèles
    admin.add_view(UserAdmin(User, db.session, name='Utilisateurs'))
    admin.add_view(RoleAdmin(Role, db.session, name='Rôles'))
    admin.add_view(DirectionAdmin(Direction, db.session, name='Directions'))
    admin.add_view(UserRoleAdmin(UserRole, db.session, name='Attribution Rôles'))

    return admin
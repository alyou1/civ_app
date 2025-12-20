from src.models import db
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    direction_id = db.Column(db.Integer, db.ForeignKey('direction.direction_id'))
    user_nom = db.Column(db.String(100), nullable=False)
    user_prenom = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_matricule = db.Column(db.String(10), unique=True, nullable=False, index=True)
    user_password = db.Column(db.String(255))
    last_connection_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    deleted_at = db.Column(db.DateTime)

    # Relations
    direction = db.relationship('Direction', backref=db.backref('users', lazy='dynamic'))
    roles = db.relationship('Role', secondary='user_role',
                            backref=db.backref('users', lazy='dynamic'),
                            lazy='dynamic')

    def set_password(self, password):
        """Hash le mot de passe"""
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe"""
        if not self.user_password:
            return False
        return check_password_hash(self.user_password, password)

    @property
    def full_name(self):
        """Retourne le nom complet"""
        return f"{self.user_prenom} {self.user_nom}"

    @property
    def is_active(self):
        """Vérifie si l'utilisateur n'est pas supprimé"""
        return self.deleted_at is None

    def __repr__(self):
        return f'{self.user_prenom} {self.user_nom} ({self.user_email})'

    def __str__(self):
        return self.full_name


class Role(db.Model):
    __tablename__ = "role"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return self.role_name

    def __str__(self):
        return self.role_name


class UserRole(db.Model):
    __tablename__ = "user_role"

    user_role_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    deleted_at = db.Column(db.DateTime)

    # Index unique pour éviter les doublons
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )

    # Relations pour Flask-Admin
    user = db.relationship('User', backref=db.backref('user_roles', lazy='dynamic'))
    role = db.relationship('Role', backref=db.backref('role_users', lazy='dynamic'))

    def __repr__(self):
        return f'UserRole(user_id={self.user_id}, role_id={self.role_id})'

    def __str__(self):
        return f'{self.user} - {self.role}'


class Direction(db.Model):
    __tablename__ = "direction"

    direction_id = db.Column(db.Integer, primary_key=True)
    direction_name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    deleted_at = db.Column(db.DateTime)

    def __repr__(self):
        return self.direction_name

    def __str__(self):
        return self.direction_name
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from src.models import db
from src.models.models import *
from src import CONFIG
import os
from dotenv import load_dotenv

def create_app():
    # Charger les variables d'environnement
    load_dotenv()

    app = Flask(__name__)

    # Configuration de base
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CONFIG['SQLALCHEMY_TRACK_MODIFICATIONS']
    app.config['SQLALCHEMY_ECHO'] = os.getenv('FLASK_ENV') == 'development'  # Log SQL en dev
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


    # Configuration JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = CONFIG['JWT_ACCESS_TOKEN_EXPIRES']
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = CONFIG['JWT_REFRESH_TOKEN_EXPIRES']

    # Configuration des sessions
    app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    if not os.getenv('DB_URI'):
        raise ValueError("❌ DB_URI n'est pas défini dans le fichier .env")
    if not os.getenv('JWT_SECRET_KEY'):
        raise ValueError("❌ JWT_SECRET_KEY n'est pas défini dans le fichier .env")

    # Init extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    with app.app_context():
        if os.getenv('FLASK_ENV') == 'development':
            db.create_all()
    # API
    from web.api.auth.views import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Initialiser Flask-Admin
    from web.admin.admin_views import init_admin
    init_admin(app)

    return app
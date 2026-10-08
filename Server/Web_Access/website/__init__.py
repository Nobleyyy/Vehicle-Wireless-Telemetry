### Flask Initialisation ###

# Package Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

## Functions ##
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'pqdjgywkgawdasfhyrtwd'      # Encryption Key
    # Configure database using an absolute path to website/database.db
    db_path = path.abspath(path.join(path.dirname(__file__), DB_NAME))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)
    # Register blueprints
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    # Import user database
    from .models import User
    create_database(app)
    # Configure login authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    app.config['TEMPLATES_AUTO_RELOAD'] = True

    @login_manager.user_loader
    def load_user(id):
        # Get user from database using their id
        return User.query.get(int(id))

    @app.context_processor
    def inject_settings():
        result = db.session.execute(
            text("""
                SELECT value
                FROM settings
                WHERE key = 'allow_signups'
            """)
        ).scalar()

        # Sign-ups are enabled if the setting doesn't exist
        signups_enabled = result is None or result == "1"

        return {
            "signups_enabled": signups_enabled
        }
    return app

def create_database(app):
    # Build the absolute path to the database file
    db_path = path.abspath(path.join(path.dirname(__file__), DB_NAME))
    database_existed = path.exists(db_path)
    
    with app.app_context():
        # Create normal application tables
        db.create_all()

        # Create settings table
        db.session.execute(
            text("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
        )
        db.session.commit()

    if not database_existed:
        print("Created Database:", db_path)

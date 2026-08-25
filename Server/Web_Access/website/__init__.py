### Flask Initialisation ###

# Package Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

    @login_manager.user_loader
    def load_user(id):
        # Get user from database using their id
        return User.query.get(int(id))

    return app


def create_database(app):
    # Build the absolute path to the database file
    db_path = path.abspath(path.join(path.dirname(__file__), DB_NAME))
    # Create the database tables if the database does not exist
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
            print("Created Database:", db_path)

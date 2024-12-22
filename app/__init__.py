from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)

    # Setting JWT
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_KEY')
    # Setting Database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize JWT
    JWTManager(app)
    # Connect DB
    db.init_app(app)

    # Register routes
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
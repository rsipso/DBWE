import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

import models
from models import db

bcrypt = Bcrypt()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key' # Use environment variable for secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///app.db' # Use environment variable for database URL
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key' # Use environment variable for JWT secret key

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Route for login page
    jwt.init_app(app)
    bcrypt.init_app(app)


    from routes.auth_routes import auth_bp
    from routes.list_routes import list_bp
    from routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(list_bp)
    app.register_blueprint(api_bp)

    return app

app = create_app()

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
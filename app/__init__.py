import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import config_by_name
from app.services.blacklist import BLACKLIST

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name='development'):
    """Fábrica de la aplicación."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in BLACKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "description": "El token ha sido revocado.",
            "error": "token_revoked"
        }), 401
    
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    return app
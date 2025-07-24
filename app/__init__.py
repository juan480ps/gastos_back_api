import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import config_by_name
from app.services.blacklist import BLACKLIST

# aca se crean las instancias principales de las extensiones que se usaran en la aplicacion.
# se crean aca para que sean accesibles desde otras partes del proyecto.

# instancia para el manejo de la base de datos con sqlalchemy.
db = SQLAlchemy()
# instancia para encriptar las contraseñas.
bcrypt = Bcrypt()
# instancia para gestionar los tokens de autenticacion jwt.
jwt = JWTManager()
# instancia para limitar la cantidad de peticiones que un usuario puede hacer, para evitar abusos.
limiter = Limiter(
    # se usa la direccion ip del usuario para identificarlo.
    key_func=get_remote_address,
    # se establecen limites por defecto: 200 peticiones por dia y 50 por hora.
    default_limits=["200 per day", "50 per hour"]
)

# aca se define la funcion 'fabrica' que crea y configura la aplicacion flask.
# este patron permite crear diferentes instancias de la app, por ejemplo, para pruebas.
def create_app(config_name='development'):
    """fabrica de la aplicacion."""
    # se crea la instancia de la aplicacion flask.
    app = Flask(__name__)
    # se cargan las configuraciones (como la base de datos, claves secretas, etc.) segun el nombre recibido.
    app.config.from_object(config_by_name[config_name])

    # se inicializan las extensiones con la instancia de la aplicacion.
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # este decorador registra una funcion que se llamara cada vez que se reciba una peticion a una ruta protegida.
    @jwt.token_in_blocklist_loader
    # la funcion comprueba si el token recibido esta en la lista negra (blacklist).
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in BLACKLIST

    # este decorador registra una funcion que se ejecutara si la funcion anterior devuelve 'true'.
    @jwt.revoked_token_loader
    # la funcion devuelve una respuesta de error indicando que el token ha sido revocado (sesion cerrada).
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "description": "El token ha sido revocado.",
            "error": "token_revoked"
        }), 401
    
    # se importa el blueprint de autenticacion que contiene las rutas de login, registro, etc.
    from app.api.auth import auth_bp
    # se registra el blueprint en la aplicacion, añadiendo el prefijo '/api' a todas sus rutas.
    app.register_blueprint(auth_bp, url_prefix='/api')

    # la funcion devuelve la instancia de la aplicacion ya configurada.
    return app